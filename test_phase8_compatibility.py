"""Phase 8 evidence and offline audience-contract boundary tests."""
import io
import json
import unittest

from intrusive_ad_model import classify
from marketer_app import Handler
from phase8_audience_contract import validate_rows
from phase8_compatibility import assess
from stp_advisory import evaluate
from threshold_engine import current_dataset_status


def review(campaign=None, text="Explore our new collection."):
    campaign = campaign or {}
    creative = classify(text)
    strategy = evaluate(campaign, creative)
    return assess(campaign, creative, strategy), strategy


class CompatibilityTests(unittest.TestCase):
    def test_default_mode_a_abstains_without_customer_file(self):
        result, strategy = review()
        self.assertEqual(result["mode"], "A")
        self.assertEqual(result["status"], "research_informed_review_only")
        for field in ("compatibility_score", "consumer_relevance_prediction", "consumer_intrusiveness_prediction",
                      "consumer_segment_assignment", "expected_incremental_conversions"):
            self.assertIsNone(result[field])
        self.assertEqual(strategy["action"], "keep_current_campaign")
        self.assertEqual(current_dataset_status()["status"], "insufficient_evidence")

    def test_creative_cues_are_not_measured_consumer_response(self):
        result, _ = review({"targeting_method": "contextual", "data_source": "page_context"},
                           "Last chance! Only 2 left! We tracked your location.")
        self.assertTrue(any("tracking" in s for s in result["creative_signals"]))
        self.assertTrue(any("Pressure" in s for s in result["creative_signals"]))
        self.assertEqual(result["evidence"]["creative_cues"], "heuristic_screen_of_observable_text")
        self.assertIsNone(result["consumer_intrusiveness_prediction"])

    def test_source_method_mismatch_and_unknown_permission_hold(self):
        for campaign in ({"targeting_method": "generic", "data_source": "first_party_behavior"},
                         {"targeting_method": "behavioral", "data_source": "first_party_behavior"},
                         {"targeting_method": "historical", "data_source": "first_party_purchase",
                          "consent_status": "yes", "audience_eligibility": "unknown"},
                         {"targeting_method": "behavioral", "data_source": "unknown",
                          "consent_status": "yes", "audience_eligibility": "yes"},
                         {"targeting_method": "contextual", "data_source": "third_party",
                          "consent_status": "yes", "audience_eligibility": "yes"}):
            with self.subTest(campaign=campaign):
                result, strategy = review(campaign)
                self.assertTrue(result["data_source_review_required"])
                self.assertEqual(strategy["action"], "hold_for_review")

    def test_declared_first_party_permission_is_not_a_fit_prediction(self):
        campaign = {"targeting_method": "behavioral", "data_source": "first_party_behavior",
                    "consent_status": "yes", "audience_eligibility": "yes", "product_category": "retail",
                    "channel": "social"}
        result, strategy = review(campaign)
        self.assertFalse(result["data_source_review_required"])
        self.assertEqual(strategy["action"], "keep_current_campaign")
        self.assertEqual(result["evidence"]["campaign_context"], "marketer_declared_unverified")
        self.assertIsNone(result["compatibility_score"])

    def test_hypothetical_best_case_never_authorizes_variants(self):
        campaign = {"targeting_method": "generic", "data_source": "none", "total_budget": 1000,
                    "committed_spend": 500, "variant_cost": 20, "management_cost": 10,
                    "segmentation_cost": 10, "contribution_margin": 40,
                    "best_incremental_conversions": 1000}
        result, strategy = review(campaign)
        self.assertEqual(strategy["action"], "keep_current_campaign")
        self.assertEqual(result["evidence"]["financial_scenarios"], "user_defined_hypotheses")
        self.assertIsNone(result["expected_incremental_conversions"])

    def test_invalid_declared_context_is_rejected(self):
        for field, value in (("product_category", "secret_category"), ("channel", 123),
                             ("data_source", "cookies_everywhere")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                review({field: value})


class AudienceContractTests(unittest.TestCase):
    def setUp(self):
        self.row = {"anonymous_customer_id": "a1b2c3d4e5f60708", "event_timestamp": "2024-01-02T10:30:00Z",
                    "event_type": "product_view", "product_category": "running_shoes",
                    "behavioral_targeting_permitted": True}

    def test_valid_in_memory_contract_returns_counts_only(self):
        result = validate_rows([self.row])
        self.assertEqual(result["status"], "schema_validated_only")
        self.assertEqual(result["event_counts"], {"product_view": 1})
        self.assertNotIn(self.row["anonymous_customer_id"], json.dumps(result))
        self.assertFalse(result["individual_response_prediction"])
        self.assertFalse(result["data_retained"])

    def test_opt_out_and_missing_permission_stop_batch(self):
        for value in (False, None, "yes"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_rows([{**self.row, "behavioral_targeting_permitted": value}])

    def test_identifiers_pii_and_unapproved_fields_fail(self):
        for change in ({"anonymous_customer_id": "person@example.com"},
                       {"anonymous_customer_id": "1234567890"},
                       {"email": "person@example.com"}, {"ip_address": "127.0.0.1"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_rows([{**self.row, **change}])

    def test_bad_timestamp_duplicate_and_missing_category_fail(self):
        for change in ({"event_timestamp": "2024-01-02T10:30:00"},
                       {"event_timestamp": "2999-01-01T00:00:00Z"},
                       {"product_category": None}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_rows([{**self.row, **change}])
        with self.assertRaises(ValueError):
            validate_rows([self.row, self.row.copy()])

    def test_ad_events_need_ad_and_campaign_codes(self):
        with self.assertRaises(ValueError):
            validate_rows([{**self.row, "event_type": "ad_impression"}])
        good = {**self.row, "event_type": "ad_impression", "campaign_id": "c1", "ad_id": "ad1"}
        self.assertEqual(validate_rows([good])["event_counts"], {"ad_impression": 1})

    def test_contract_exposes_no_cross_dataset_join(self):
        result = validate_rows([self.row])
        self.assertNotIn("survey_segment", result)
        self.assertNotIn("privacy_concern", result)


class CompatibilityRouteTests(unittest.TestCase):
    def request(self, payload):
        handler = Handler.__new__(Handler)
        handler.path = "/api/analyze"
        handler.headers = {"Content-Type": "application/json"}
        body = json.dumps(payload).encode()
        handler.headers["Content-Length"] = str(len(body))
        handler.rfile = io.BytesIO(body)
        out = {}
        handler.send_bytes = lambda status, data, mime: out.update(status=status, body=data)
        handler.do_POST()
        return out["status"], json.loads(out["body"])

    def test_legacy_route_stays_intact_and_campaign_adds_review(self):
        status, legacy = self.request({"text": "Discover our collection."})
        self.assertEqual(status, 200)
        self.assertNotIn("compatibility", legacy)
        status, current = self.request({"text": "Discover our collection.", "campaign": {}})
        self.assertEqual(status, 200)
        self.assertEqual(current["tier"], legacy["tier"])
        self.assertEqual(current["compatibility"]["five_level_threshold_status"], "insufficient_evidence")
        self.assertIsNone(current["compatibility"]["compatibility_score"])


if __name__ == "__main__":
    unittest.main()
