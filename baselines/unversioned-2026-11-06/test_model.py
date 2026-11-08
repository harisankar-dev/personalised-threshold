import unittest
import json
from pathlib import Path

from intrusive_ad_model import classify


class TierTests(unittest.TestCase):
    def test_generic_offer_is_low(self):
        result = classify("Shop our new fall collection")
        self.assertEqual(result["tier"], "low_intrusive")
        self.assertEqual(result["score_out_of_10"], 0)
        self.assertEqual(result["recommendations"], [])

    def test_generic_you_is_not_personal_data(self):
        self.assertEqual(classify("Your dream vacation starts here")["tier"], "low_intrusive")

    def test_cart_reference_is_moderate(self):
        result = classify("Your cart is waiting")
        self.assertEqual(result["tier"], "moderate_intrusive")
        self.assertEqual(result["score_out_of_10"], 3)

    def test_single_observed_behavior_is_moderate(self):
        result = classify("We noticed you searched for shoes")
        self.assertEqual(result["tier"], "moderate_intrusive")
        self.assertEqual(result["score_out_of_10"], 3)

    def test_sensitive_fact_is_high(self):
        self.assertEqual(classify("Your credit score is low")["tier"], "high_intrusive")

    def test_precise_location_is_high(self):
        self.assertEqual(classify("A deal near your home today")["tier"], "high_intrusive")

    def test_empty_input_requires_review(self):
        self.assertEqual(classify("")["tier"], "needs_review")

    def test_generic_city_ad_is_not_location_tracking(self):
        self.assertEqual(classify("Visit Goa this summer. Book today.")["tier"], "low_intrusive")

    def test_generic_health_product_is_not_personal_health_fact(self):
        self.assertEqual(classify("Discover our health products")["tier"], "low_intrusive")

    def test_paraphrases_of_data_use_are_detected(self):
        examples = [
            ("We saw that you were checking running shoes yesterday.", "moderate_intrusive"),
            ("You were browsing sneakers last night. Check these out.", "moderate_intrusive"),
            ("Based on your previous order, we picked a matching pair.", "moderate_intrusive"),
            ("Get deals near you.", "moderate_intrusive"),
            ("We know you are in Goa right now.", "high_intrusive"),
            ("We monitored your visits to shoe sites.", "high_intrusive"),
        ]
        for text, expected in examples:
            with self.subTest(text=text):
                self.assertEqual(classify(text)["tier"], expected)

    def test_multiple_signals_raise_risk(self):
        result = classify("Based on your recent searches and past purchases, explore deals near you.")
        self.assertEqual(result["tier"], "high_intrusive")
        advice_cues = {item["cue"] for item in result["recommendations"]}
        self.assertIn("browsing_history", advice_cues)
        self.assertIn("purchase_history", advice_cues)
        self.assertIn("combined_signals", advice_cues)

    def test_consent_advice_requires_more_than_copy_edit(self):
        result = classify("Shop the new collection", "consent: no")
        self.assertIn("Do not use this targeting", result["recommendations"][0]["action"])

    def test_aggressive_image_ocr_text_is_high_without_privacy_cues(self):
        ocr_text = (
            "LAST CHANCE 00:00: 03:32. ALERT!!! THEY DO NOT WANT YOU TO SEE THIS!!! "
            "CLICK THE LINK NOW before the timer runs out!!! Only 14 left!!! "
            "SHOP NOW - 99% OFF TODAY ONLY!"
        )
        result = classify(ocr_text)
        self.assertEqual(result["tier"], "high_intrusive")
        self.assertEqual(result["score_out_of_10"], 10)
        self.assertEqual(result["privacy_score"], 0)
        self.assertGreaterEqual(result["pressure_score"], 10)
        self.assertIn("countdown_pressure", {item["cue"] for item in result["evidence"]})

    def test_normal_sale_is_low_pressure(self):
        result = classify("Shop our new watches. Save 20% today.")
        self.assertEqual(result["tier"], "low_intrusive")
        self.assertEqual(result["pressure_score"], 0)

    def test_survey_sanity_conditions(self):
        fixture = json.loads((Path(__file__).parent / "survey_sanity_cases.json").read_text(encoding="utf-8"))
        scores = {}
        for item in fixture["cases"]:
            with self.subTest(condition=item["condition"]):
                result = classify(item["ad_text"])
                self.assertEqual(result["tier"], item["expected_tier"])
                self.assertGreaterEqual(result["score_out_of_10"], item["score_range"][0])
                self.assertLessEqual(result["score_out_of_10"], item["score_range"][1])
                scores[item["condition"]] = result["score_out_of_10"]
        self.assertLess(scores["A"], scores["B"])
        self.assertLess(scores["B"], scores["C"])
        self.assertLessEqual(scores["C"], scores["D"])
        self.assertLess(scores["D"], scores["E"])
        self.assertLess(scores["E"], scores["F"])


if __name__ == "__main__":
    unittest.main()
