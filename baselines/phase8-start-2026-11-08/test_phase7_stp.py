"""Decision and financial boundary checks for the exploratory Phase 7 advisory."""
import io
import json
import unittest

from intrusive_ad_model import classify, predict
from marketer_app import Handler
from stp_advisory import evaluate, survey_personas
from threshold_engine import current_dataset_status


def creative(text="Discover our new collection."):
    return classify(text)


class StrategyDecisionTests(unittest.TestCase):
    def test_missing_financial_inputs_keep_existing_option_without_fabricated_results(self):
        result = evaluate({}, creative())
        self.assertEqual(result["action"], "keep_current_campaign")
        self.assertEqual(result["options"][0]["key"], "keep_current_campaign")
        self.assertIsNone(result["options"][1]["incremental_implementation_cost"])
        self.assertIsNone(result["options"][3]["break_even_incremental_conversions"])
        self.assertIsNone(result["scenario"]["results"]["central"]["net_incremental_value"])
        self.assertFalse(result["validated_incremental_performance"])

    def test_cheap_revision_is_advisory_within_budget_and_extra_variants_are_not_recommended(self):
        inputs = {"total_budget": "1000", "committed_spend": "900", "revision_cost": "20",
                  "targeting_cost": "40", "variant_cost": "80", "segmentation_cost": "50",
                  "management_cost": "30", "contribution_margin": "12"}
        result = evaluate(inputs, creative("Last chance! Only 3 left!"))
        self.assertEqual(result["action"], "revise_one_creative")
        self.assertEqual(result["available_budget_headroom"], "100.00")
        self.assertEqual(result["options"][1]["break_even_incremental_conversions"], 2)
        self.assertTrue(result["options"][1]["budget_feasible"])
        self.assertFalse(result["options"][3]["budget_feasible"])
        self.assertEqual(result["options"][3]["permission_status"], "Unverified")

    def test_hypothetical_scenarios_use_margin_and_cost_but_do_not_trigger_rollout(self):
        inputs = {"total_budget": 1000, "committed_spend": 700, "variant_cost": 90,
                  "management_cost": 20, "segmentation_cost": 40, "contribution_margin": 30,
                  "worst_incremental_conversions": 0, "central_incremental_conversions": 5,
                  "best_incremental_conversions": 9}
        result = evaluate(inputs, creative())
        self.assertEqual(result["action"], "keep_current_campaign")
        self.assertEqual(result["options"][3]["break_even_incremental_conversions"], 5)
        self.assertEqual(result["scenario"]["results"]["worst"]["net_incremental_value"], "-150.00")
        self.assertEqual(result["scenario"]["results"]["central"]["net_incremental_value"], "0.00")
        self.assertEqual(result["scenario"]["results"]["best"]["net_incremental_value"], "120.00")

    def test_multiple_variants_cost_more_and_budget_fragmentation_does_not_override_keep(self):
        result = evaluate({"total_budget": 500, "committed_spend": 470,
                           "variant_cost": 25, "management_cost": 10,
                           "segmentation_cost": 5, "variant_count": 3,
                           "audience_reach": 100}, creative())
        self.assertEqual(result["action"], "keep_current_campaign")
        self.assertFalse(result["options"][3]["budget_feasible"])
        self.assertEqual(result["options"][4]["incremental_implementation_cost"], "90.00")
        self.assertFalse(result["options"][4]["budget_feasible"])
        self.assertFalse(result["validated_audience_segment"])

    def test_consent_and_eligibility_gate_behavioral_and_sensitive_targeting(self):
        for input_data in ({"targeting_method": "behavioral", "consent_status": "unknown"},
                           {"targeting_method": "demographic", "consent_status": "unknown"},
                           {"targeting_method": "historical", "consent_status": "no"},
                           {"targeting_method": "combined", "consent_status": "yes", "audience_eligibility": "unknown"},
                           {"targeting_method": "sensitive", "consent_status": "yes", "audience_eligibility": "yes"},
                           {"targeting_method": "generic", "audience_eligibility": "no"}):
            with self.subTest(input_data=input_data):
                self.assertEqual(evaluate(input_data, creative())["action"], "hold_for_review")
                self.assertEqual(evaluate(input_data, creative())["options"][2]["permission_status"], "Hold for review")

    def test_unassessed_image_and_unaffordable_revision_hold_for_review(self):
        self.assertEqual(evaluate({}, {"tier": "needs_review", "evidence": []})["action"], "hold_for_review")
        inputs = {"total_budget": 100, "committed_spend": 95, "revision_cost": 10}
        self.assertEqual(evaluate(inputs, creative("Last chance!"))["action"], "hold_for_review")

    def test_invalid_cost_and_scenario_inputs_fail_explicitly(self):
        invalid = ({"total_budget": "NaN"}, {"total_budget": -1},
                   {"total_budget": 10, "committed_spend": 11},
                   {"contribution_margin": "-2"}, {"conversion_rate_pct": 110},
                   {"variant_count": 1}, {"audience_reach": 2.5},
                   {"worst_incremental_conversions": 5, "central_incremental_conversions": 4,
                    "best_incremental_conversions": 6},
                   {"worst_incremental_conversions": 5, "best_incremental_conversions": 4})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate(value, creative())

    def test_personas_are_aggregate_and_threshold_still_abstains(self):
        personas = survey_personas()
        self.assertEqual(personas["status"], "descriptive_only")
        self.assertEqual(personas["sources"]["genz"]["respondents"], 296)
        self.assertEqual(sum(personas["sources"]["romano_han"]["counts"].values()), 837)
        self.assertEqual(current_dataset_status()["status"], "insufficient_evidence")

    def test_awareness_goal_does_not_turn_conversion_arithmetic_into_a_success_claim(self):
        result = evaluate({"objective": "awareness", "revision_cost": 30,
                           "contribution_margin": 15}, creative("Last chance!"))
        self.assertEqual(result["options"][1]["break_even_incremental_conversions"], 2)
        self.assertTrue(any("not a validated success measure" in note for note in result["warnings"]))


class StrategyRouteTests(unittest.TestCase):
    def request(self, payload):
        handler = Handler.__new__(Handler)
        handler.path = "/api/analyze"
        handler.headers = {"Content-Type": "application/json"}
        body = json.dumps(payload).encode("utf-8")
        handler.headers["Content-Length"] = str(len(body))
        handler.rfile = io.BytesIO(body)
        captured = {}
        handler.send_bytes = lambda status, data, mime: captured.update(status=status, body=data)
        handler.do_POST()
        return captured["status"], json.loads(captured["body"])

    def test_existing_api_is_preserved_and_campaign_adds_separate_advisory(self):
        status, old = self.request({"text": "Discover our new collection."})
        self.assertEqual(status, 200)
        self.assertNotIn("strategy", old)
        status, new = self.request({"text": "Discover our new collection.", "campaign": {}})
        self.assertEqual(status, 200)
        self.assertEqual(new["tier"], old["tier"])
        self.assertEqual(new["threshold_decision"]["status"], "insufficient_evidence")
        self.assertEqual(new["strategy"]["action"], "keep_current_campaign")
        self.assertEqual(new["strategy"]["survey_personas"]["status"], "descriptive_only")

    def test_invalid_campaign_is_a_client_error(self):
        status, body = self.request({"text": "Discover our new collection.",
                                     "campaign": {"total_budget": "infinite"}})
        self.assertEqual(status, 400)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
