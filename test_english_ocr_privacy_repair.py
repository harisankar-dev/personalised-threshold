"""Targeted privacy-language repair; examples test software rules, not consumers."""
import unittest

from intrusive_ad_model import classify


class PrivacyCueRepairTests(unittest.TestCase):
    @staticmethod
    def cues(text):
        return {row["cue"] for row in classify(text)["evidence"]}

    def test_known_location_diagnostic(self):
        result = classify("We know where you live. Time starts now.")
        self.assertIn("precise_location", self.cues("We know where you live. Time starts now."))
        self.assertEqual(result["tier"], "high_intrusive")
        self.assertEqual(result["score_out_of_10"], 6)

    def test_fresh_explicit_activity_claims(self):
        self.assertIn("browsing_history", self.cues("We know what you searched for yesterday."))
        self.assertIn("explicit_surveillance", self.cues("We've tracked your activity across our site."))
        self.assertIn("direct_identifier", self.cues("We know your home address."))

    def test_ordinary_seller_and_form_language(self):
        ordinary = [
            "Visit our store.",
            "Our address is 10 King Street.",
            "Contact our support team at help@example.com.",
            "Enter your phone number to register.",
        ]
        for text in ordinary:
            with self.subTest(text=text):
                self.assertFalse(self.cues(text) & {
                    "precise_location", "explicit_surveillance", "browsing_history", "direct_identifier"})

    def test_negation_quotation_and_example_context(self):
        guarded = [
            "We do not know where you live.",
            "The campaign quoted 'We know where you live' as a bad example.",
            "For example, do not say 'We know what you searched for.'",
            "The phrase 'We've tracked your activity' is misleading.",
        ]
        for text in guarded:
            with self.subTest(text=text):
                self.assertFalse(self.cues(text) & {
                    "precise_location", "explicit_surveillance", "browsing_history"})


if __name__ == "__main__":
    unittest.main()
