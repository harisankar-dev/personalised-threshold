"""Phase 13 context, urgency, OCR and preservation regression tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from intrusive_ad_model import classify, ocr_image, predict
from phase13_validation.evaluate import normalize
from threshold_engine import current_dataset_status

ROOT = Path(__file__).resolve().parent


def cues(text: str) -> set[str]:
    return {item["cue"] for item in classify(text)["evidence"]}


class IdentifierContextTests(unittest.TestCase):
    def test_seller_and_example_contacts_do_not_claim_viewer_identity(self):
        samples = ["Call 9876543210 to order.", "Email careers@example.com to apply.",
                   "WhatsApp us at +91 98765 43210.", "Contact our support team at help@example.com.",
                   "Visit our showroom at 123 Main Street.",
                   "For example, email sample@example.com.",
                   "Enter your phone number to sign up.",
                   "The phrase 'your email is alice@example.com' is a sample.",
                   "We don't say your personal email in our ads."]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertNotIn("direct_identifier", cues(sample))

    def test_viewer_identity_claim_is_preserved(self):
        samples = ["We know your phone number.", "Your personal email is alice@example.com.",
                   "We identified your account.", "We know your home address."]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertIn("direct_identifier", cues(sample))

    def test_unowned_contact_requests_review_without_six_point_alert(self):
        result = classify("alice@unknown-domain.net")
        self.assertEqual("needs_review", result["tier"])
        self.assertIsNone(result["score"])
        self.assertTrue(result["review_flags"])


class UrgencyTests(unittest.TestCase):
    def test_explicit_deadlines(self):
        samples = ["Limited time offer", "Offer ends tonight", "Sale ends tomorrow",
                   "This weekend only", "Final day", "Offer valid until Friday",
                   "Ends at midnight", "24-hour special", "Only until Sunday", "Last day to claim"]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertIn("urgent_call_to_action", cues(sample))

    def test_unrelated_negated_or_quoted_uses(self):
        samples = ["We don't use limited-time offers.", "Avoid saying limited time offer.",
                   "Our office has limited opening hours.", "This article explains sales deadlines.",
                   "Limited edition product.", "The phrase 'last chance' is misleading."]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertNotIn("urgent_call_to_action", cues(sample))

    def test_time_inventory_and_discount_are_distinct_and_nonduplicated(self):
        result = classify("Limited time offer. Limited time sale. Only 3 left. 90% off.")
        names = [e["cue"] for e in result["evidence"]]
        self.assertEqual(names.count("urgent_call_to_action"), 1)
        self.assertIn("scarcity_claim", names)
        self.assertIn("extreme_discount", names)


class OCRAndResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / ".ocr_tmp").mkdir(exist_ok=True)

    def test_clear_local_english_image_and_threshold_abstention(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".ocr_tmp") as folder:
            path = Path(folder) / "clear.png"
            image = Image.new("RGB", (800, 220), "white")
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 52)
            draw.text((25, 30), "LIMITED TIME OFFER", fill="black", font=font)
            draw.text((25, 115), "SHOP TODAY", fill="black", font=font)
            image.save(path)
            ocr = ocr_image(path)
            self.assertIn("limited time offer", normalize(ocr["text"]))
            result = predict(image=path)
            self.assertIn("urgent_call_to_action", {e["cue"] for e in result["evidence"]})
            self.assertEqual("insufficient_evidence", result["threshold_decision"]["status"])
            self.assertIsNone(result["threshold_decision"]["recommended_level"])

    def test_empty_image_abstains(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".ocr_tmp") as folder:
            path = Path(folder) / "blank.png"
            Image.new("RGB", (600, 240), "white").save(path)
            result = predict(image=path)
            self.assertEqual("needs_review", result["tier"])
            self.assertIsNone(result["score"])

    def test_fresh_ids_exclude_phase12(self):
        fresh = json.loads((ROOT / "phase13_validation/real_ad_reference_v1.json").read_text(encoding="utf-8"))["cases"]
        previous = json.loads((ROOT / "phase12_validation/real_ad_labels_v1.json").read_text(encoding="utf-8"))["cases"]
        self.assertFalse({c["id"] for c in fresh} & {c["id"] for c in previous})
        self.assertEqual(6, sum(c["split"] == "test" for c in fresh))
        self.assertEqual(6, sum(c["split"] == "development" for c in fresh))
        self.assertEqual("insufficient_evidence", current_dataset_status()["status"])


if __name__ == "__main__":
    unittest.main()
