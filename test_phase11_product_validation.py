"""Phase 11 synthetic product decisions and financial boundary checks."""

import json
import unittest
from pathlib import Path

from intrusive_ad_model import classify
from phase11_validation.evaluate_creative import evaluate as evaluate_cues
from stp_advisory import evaluate
from threshold_engine import current_dataset_status


ROOT = Path(__file__).resolve().parent


class CreativeDiagnosticTests(unittest.TestCase):
    def test_frozen_fixture_and_targeted_negation_repairs(self):
        baseline = json.loads((ROOT / "phase11_validation/creative_baseline_v1.json").read_text(encoding="utf-8"))
        current = evaluate_cues()
        self.assertEqual(current["fixture_sha256"], baseline["fixture_sha256"])
        self.assertEqual(current["n_cases"], 26)
        self.assertLess(current["overall"]["fp"], baseline["overall"]["fp"])
        self.assertEqual(current["overall"]["fn"], baseline["overall"]["fn"])
        for text, targeting in (
            ("We never said 'we tracked you'.", ""),
            ("Never say 'last chance' in our ads.", ""),
            ("Explore our collection.", "We do not use purchase history."),
            ("Explore our collection.", "Page context only, not browsing history."),
        ):
            with self.subTest(text=text, targeting=targeting):
                self.assertEqual([], classify(text, targeting)["evidence"])

    def test_positive_assertion_after_denial_still_matches(self):
        cues = {item["cue"] for item in classify(
            "Explore our collection.",
            "We do not use purchase history; we use browsing history.")["evidence"]}
        self.assertEqual({"browsing_history"}, cues)
        self.assertIn("no_consent", {item["cue"] for item in
                                  classify("We used your location without your consent.")["evidence"]})


class DecisionMatrixTests(unittest.TestCase):
    def test_eighteen_campaign_states(self):
        cases = [
            ("generic", {}, "Explore our collection.", "keep_current_campaign"),
            ("low_unknown_money", {"targeting_method": "generic", "data_source": "none"}, "Explore our collection.", "keep_current_campaign"),
            ("moderate_one_revision", {"total_budget": 100, "committed_spend": 80, "revision_cost": 10}, "Last chance.", "revise_one_creative"),
            ("high_no_headroom", {"total_budget": 100, "committed_spend": 100, "revision_cost": 10}, "We tracked you.", "hold_for_review"),
            ("unknown_personal_source", {"targeting_method": "behavioral", "consent_status": "yes", "audience_eligibility": "yes"}, "Explore our collection.", "hold_for_review"),
            ("source_mismatch", {"targeting_method": "generic", "data_source": "first_party_behavior"}, "Explore our collection.", "hold_for_review"),
            ("behavioral_consent_unknown", {"targeting_method": "behavioral", "data_source": "first_party_behavior"}, "Explore our collection.", "hold_for_review"),
            ("historical_eligibility_unknown", {"targeting_method": "historical", "data_source": "first_party_purchase", "consent_status": "yes"}, "Explore our collection.", "hold_for_review"),
            ("sensitive_method", {"targeting_method": "sensitive"}, "Explore our collection.", "hold_for_review"),
            ("self_reported_permission", {"targeting_method": "behavioral", "data_source": "first_party_behavior", "consent_status": "yes", "audience_eligibility": "yes"}, "Explore our collection.", "keep_current_campaign"),
            ("conflict", {"targeting_method": "contextual", "data_source": "first_party_purchase", "consent_status": "yes", "audience_eligibility": "yes"}, "Explore our collection.", "hold_for_review"),
            ("missing_margin", {"total_budget": 100, "committed_spend": 50, "revision_cost": 10}, "Explore our collection.", "keep_current_campaign"),
            ("positive_hypothesis", {"best_incremental_conversions": 99, "variant_cost": 10, "management_cost": 2, "segmentation_cost": 2, "contribution_margin": 50}, "Explore our collection.", "keep_current_campaign"),
            ("tiny_audience", {"audience_reach": 2, "variant_count": 3}, "Explore our collection.", "keep_current_campaign"),
            ("variants_over_budget", {"total_budget": 100, "committed_spend": 90, "variant_cost": 20, "management_cost": 10, "segmentation_cost": 5, "variant_count": 3}, "Explore our collection.", "keep_current_campaign"),
            ("revision_over_budget", {"total_budget": 100, "committed_spend": 90, "revision_cost": 11}, "Only 3 left!", "hold_for_review"),
            ("permission_beats_gain", {"targeting_method": "behavioral", "data_source": "first_party_behavior", "consent_status": "no", "best_incremental_conversions": 999, "variant_cost": 1, "management_cost": 1, "segmentation_cost": 1, "contribution_margin": 100}, "Explore our collection.", "hold_for_review"),
            ("no_consent_copy", {"targeting_method": "generic", "data_source": "none"}, "We used your location without your consent.", "hold_for_review"),
        ]
        self.assertEqual(18, len(cases))
        for name, campaign, text, expected in cases:
            with self.subTest(name=name):
                result = evaluate(campaign, classify(text))
                self.assertEqual(expected, result["action"])
                self.assertEqual("keep_current_campaign", result["options"][0]["key"])
                self.assertFalse(result["validated_incremental_performance"])
                self.assertEqual("insufficient_evidence", result["five_level_threshold_status"])
        self.assertEqual("hold_for_review", evaluate({}, {"tier": "needs_review", "evidence": []})["action"])
        self.assertEqual("insufficient_evidence", current_dataset_status()["status"])

    def test_unknown_source_warning_and_tiny_audience_warning(self):
        unknown = evaluate({}, classify("Explore our collection."))
        self.assertIn("Review missing targeting information", unknown["reason"])
        tiny = evaluate({"audience_reach": 2, "variant_count": 3}, classify("Explore our collection."))
        self.assertTrue(any("smaller than" in warning for warning in tiny["warnings"]))


class BudgetStressTests(unittest.TestCase):
    def test_exact_costs_headroom_and_break_even(self):
        result = evaluate({"total_budget": "1000.00", "committed_spend": "900.00",
                           "revision_cost": "20.00", "targeting_cost": "30.00",
                           "variant_cost": "40.00", "segmentation_cost": "15.00",
                           "management_cost": "5.00", "variant_count": 3,
                           "contribution_margin": "12.00", "scenario_option": "one_variant",
                           "worst_incremental_conversions": 0,
                           "central_incremental_conversions": 5,
                           "best_incremental_conversions": 6}, classify("Explore our collection."))
        self.assertEqual("100.00", result["available_budget_headroom"])
        self.assertEqual(["0.00", "20.00", "35.00", "60.00", "140.00"],
                         [item["incremental_implementation_cost"] for item in result["options"]])
        self.assertEqual([0, 2, 3, 5, 12],
                         [item["break_even_incremental_conversions"] for item in result["options"]])
        self.assertEqual([True, True, True, True, False],
                         [item["budget_feasible"] for item in result["options"]])
        self.assertEqual("0.00", result["scenario"]["results"]["central"]["net_incremental_value"])
        self.assertEqual("12.00", result["scenario"]["results"]["best"]["net_incremental_value"])
        self.assertEqual("keep_current_campaign", result["action"])

    def test_fractional_cents_and_invalid_amounts_rejected(self):
        for campaign in ({"revision_cost": "0.005"}, {"total_budget": "0.001"},
                         {"contribution_margin": "1.234"}, {"total_budget": "NaN"},
                         {"committed_spend": -1}, {"total_budget": 0, "committed_spend": 1},
                         {"currency": "inr"}, {"variant_count": 1},
                         {"worst_incremental_conversions": -1}):
            with self.subTest(campaign=campaign), self.assertRaises(ValueError):
                evaluate(campaign, classify("Explore our collection."))

    def test_zero_and_unknown_margin_and_overspend_behavior(self):
        for margin in (0, None):
            campaign = {"total_budget": 0, "committed_spend": 0, "revision_cost": 10,
                        "variant_cost": 20, "management_cost": 5, "segmentation_cost": 5}
            if margin is not None:
                campaign["contribution_margin"] = margin
            result = evaluate(campaign, classify("Last chance!"))
            self.assertEqual("hold_for_review", result["action"])
            self.assertIsNone(result["options"][1]["break_even_incremental_conversions"])
            self.assertFalse(result["options"][1]["budget_feasible"])

    def test_large_amounts_keep_decimal_arithmetic_and_currency_label(self):
        result = evaluate({"currency": "USD", "total_budget": "1000000000000.00",
                           "committed_spend": "999999999990.00",
                           "revision_cost": "9.99", "contribution_margin": "0.01"},
                          classify("Last chance!"))
        self.assertEqual("USD", result["currency"])
        self.assertEqual("10.00", result["available_budget_headroom"])
        self.assertEqual("0.01", result["options"][1]["remaining_budget_after_option"])
        self.assertEqual(999, result["options"][1]["break_even_incremental_conversions"])
        self.assertEqual("revise_one_creative", result["action"])


if __name__ == "__main__":
    unittest.main()
