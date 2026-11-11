"""Phase 14 OCR selection and bounded creative-cue regressions."""
import unittest

from intrusive_ad_model import _select_ocr_transcript, classify, predict


class TestPhase14OCRSelection(unittest.TestCase):
    def test_second_pass_never_appended_to_readable_first(self):
        first = {"text": "SMASHING PRICES", "confidence": 48}
        noisy = {"text": "SMASHING PRICES\nGIPR\nMA\nSMASH1NG", "confidence": 89}
        result = _select_ocr_transcript(first, noisy)
        self.assertEqual(result["text"], "SMASHING PRICES")
        self.assertEqual(result["passes"], 1)

    def test_reliable_rescue_only_after_no_latin_words(self):
        first = {"text": "# 42 !!", "confidence": 0}
        second = {"text": "Final sale ends this Friday", "confidence": 72}
        result = _select_ocr_transcript(first, second)
        self.assertEqual(result["text"], second["text"])
        self.assertTrue(result["rescue_accepted"])
        self.assertIsNotNone(result["quality_warning"])

    def test_short_second_pass_is_not_promoted(self):
        result = _select_ocr_transcript({"text": "", "confidence": 0},
                                        {"text": "GIPR MA", "confidence": 90})
        self.assertEqual(result["text"], "")
        self.assertFalse(result["rescue_accepted"])

    def test_long_low_confidence_transcript_still_abstains(self):
        result = _select_ocr_transcript({"text": "garble " * 150, "confidence": 20})
        self.assertTrue(result["severely_garbled"])
        self.assertIn("severely garbled", result["quality_warning"])


class TestPhase14CueBoundaries(unittest.TestCase):
    def cues(self, text):
        return {item["cue"] for item in classify(text)["evidence"]}

    def test_development_ad_deadline(self):
        self.assertIn("urgent_call_to_action", self.cues("As this deal is for a limited time only"))

    def test_negated_deadline(self):
        self.assertNotIn("urgent_call_to_action", self.cues("We don't use limited time only claims."))

    def test_seller_contact_is_not_viewer_identity(self):
        self.assertNotIn("direct_identifier", self.cues("Mail us your orders at once. Call 555-555-1234."))

    def test_threshold_remains_unvalidated(self):
        result = predict(text="Explore our collection")
        self.assertEqual(result["threshold_decision"]["status"], "insufficient_evidence")
        self.assertIsNone(result["threshold_decision"]["recommended_level"])


if __name__ == "__main__":
    unittest.main()
