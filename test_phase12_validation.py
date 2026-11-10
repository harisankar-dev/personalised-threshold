"""Regression guards for the Phase 12 data and environment evidence."""

import json
import os
from pathlib import Path
import unittest

from phase12_validation.evaluate_real_ads import CUES, LABELS, evaluate, measures


ROOT = Path(__file__).resolve().parent


class Phase12ValidationTests(unittest.TestCase):
    def test_frozen_labels_are_disjoint_and_use_known_cues(self):
        cases = json.loads(LABELS.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 25)
        self.assertEqual(len({c["id"] for c in cases}), 25)
        self.assertEqual(sum(c["split"] == "development" for c in cases), 8)
        self.assertEqual(sum(c["split"] == "test" for c in cases), 17)
        self.assertEqual(sum(not c["assessable"] for c in cases), 6)
        for case in cases:
            self.assertIn(case["split"], {"development", "test"})
            self.assertFalse(set(case["present"]) & set(case["ambiguous"]))
            self.assertTrue((set(case["present"]) | set(case["ambiguous"])) <= set(CUES))

    def test_zero_positive_predictions_do_not_create_precision(self):
        from collections import Counter
        result = measures(Counter(tp=0, fp=0, fn=2, tn=195))
        self.assertIsNone(result["precision"])
        self.assertEqual(result["recall"], 0)
        self.assertEqual(result["recall_wilson_95"], [0.0, 0.6576])

    def test_real_ad_baseline_reproduces_when_source_files_available(self):
        csv_path = os.environ.get("PHASE12_AD_CSV")
        zip_path = os.environ.get("PHASE12_AD_ZIP")
        if not csv_path or not zip_path:
            self.skipTest("Set PHASE12_AD_CSV and PHASE12_AD_ZIP to downloaded licensed source files")
        current = evaluate(Path(csv_path), Path(zip_path))
        saved = json.loads((ROOT / "phase12_validation" / "real_ad_baseline_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(current, saved)


if __name__ == "__main__":
    unittest.main()
