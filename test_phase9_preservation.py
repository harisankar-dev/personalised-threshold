"""Regression guard for pre-Phase-9 secondary sources and saved artifacts."""

import json
import tempfile
import unittest
from pathlib import Path

from phase9_research.preservation import MANIFEST, ROOT, verify


class Phase9PreservationTests(unittest.TestCase):
    def test_original_sources_models_and_results_are_unchanged(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("phase9-start-2026-11-08", manifest["checkpoint_git_tag"])
        self.assertEqual([], verify(manifest, ROOT))

    def test_verifier_detects_changed_source(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder)
            self.assertTrue(root.resolve().is_relative_to(ROOT.resolve()))
            source = root / "source.csv"
            source.write_bytes(b"original")
            manifest = {"entries": [{"path": "source.csv", "bytes": 8,
                                     "sha256": "not-the-original-hash"}]}
            self.assertEqual(["changed: source.csv"], verify(manifest, root))


if __name__ == "__main__":
    unittest.main()
