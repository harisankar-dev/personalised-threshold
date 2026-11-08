"""Synthetic-only checks for Phase 10 research intake and repository safety."""

import json
import subprocess
import unittest
from pathlib import Path

from phase10_research.intake import (
    EligibilityError, SOURCE_ID, minimize_rows, require_rights, respondent_disjoint_split,
    treatment_label, validate_features, validate_minimized_rows,
)
from phase10_research.staging_guard import restricted_path, staged_restricted_paths


ROOT = Path(__file__).resolve().parent


def synthetic_rights():
    return {
        "source_id": SOURCE_ID,
        "evidence_type": "written_grant",
        "evidence_url_or_record": "synthetic-test-grant",
        "reviewed_by": "synthetic-test-reviewer",
        "academic_analysis": True,
        "local_retention": True,
        "model_training": True,
        "derivative_artifacts": True,
        "publication": True,
        "privacy_review": True,
    }


def synthetic_row(key="synthetic-01", targ=0, trans=0):
    return {
        "ResponseId": key, "Targ": targ, "Trans": trans,
        "PPI": 3.0, "PPR": 4.0, "PP": 3.5, "ITC": 2.0,
        "IPAddress": "synthetic-not-an-ip", "Latitude": "synthetic",
        "Email": "synthetic-not-an-email", "BirthYear": 2000,
        "FreeText": "synthetic fixture only",
    }


class Phase10IntakeTests(unittest.TestCase):
    def test_actual_osf_rights_status_blocks_processing(self):
        status = json.loads((ROOT / "phase10_research/rights_status.json").read_text(encoding="utf-8"))
        with self.assertRaises(EligibilityError):
            minimize_rows([synthetic_row()], study=1, rights=status)

    def test_rights_gate_requires_every_intended_use(self):
        record = synthetic_rights()
        require_rights(record)
        for field in ("academic_analysis", "local_retention", "model_training",
                      "derivative_artifacts", "publication", "privacy_review"):
            changed = {**record, field: False}
            with self.subTest(field=field), self.assertRaises(EligibilityError):
                require_rights(changed)
        with self.assertRaises(EligibilityError):
            require_rights({**record, "evidence_type": "public_download"})
        with self.assertRaises(EligibilityError):
            require_rights({**record, "source_id": "unrelated source"})

    def test_allowlist_removes_identifiers_quasi_identifiers_and_text(self):
        clean = minimize_rows([synthetic_row()], study=1, rights=synthetic_rights())
        self.assertEqual({"Targ", "Trans", "PPI", "PPR", "PP", "ITC"}, set(clean[0]))
        self.assertEqual(0, clean[0]["Targ"])
        validate_minimized_rows(clean)
        with self.assertRaises(EligibilityError):
            validate_minimized_rows([{**clean[0], "BirthYear": 2000}])

    def test_prelaunch_feature_gate_rejects_post_exposure_and_identifiers(self):
        self.assertEqual(("Targ", "Trans"), validate_features(["Targ", "Trans"]))
        for name in ("PPI", "PPR", "PP", "ITC", "ResponseId", "IPAddress"):
            with self.subTest(name=name), self.assertRaises(EligibilityError):
                validate_features(["Targ", name])

    def test_study_specific_treatment_coding(self):
        self.assertEqual(("no_location_targeting", "no_disclosure"), treatment_label(1, 0, 0))
        self.assertEqual(("country_location_targeting", "information_use_disclosure"),
                         treatment_label(2, 0, 1))
        self.assertEqual(("city_location_targeting", "no_disclosure"), treatment_label(2, 1, 0))
        with self.assertRaises(EligibilityError):
            treatment_label(3, 0, 0)

    def test_missing_invalid_and_duplicate_records_fail_closed(self):
        bad = [
            {**synthetic_row(), "PPI": None},
            {**synthetic_row(), "PPI": float("nan")},
            {**synthetic_row(), "Targ": 2},
            {**synthetic_row(), "ResponseId": ""},
        ]
        for row in bad:
            with self.subTest(row=row.get("PPI")), self.assertRaises(EligibilityError):
                minimize_rows([row], study=1, rights=synthetic_rights())
        with self.assertRaises(EligibilityError):
            minimize_rows([synthetic_row(), synthetic_row()], study=1, rights=synthetic_rights())

    def test_respondent_split_keeps_repeats_and_cells_separate(self):
        rows, keys = [], []
        for targ in (0, 1):
            for trans in (0, 1):
                for group in range(4):
                    for _ in range(2):
                        rows.append({"Targ": targ, "Trans": trans})
                        keys.append(f"synthetic-{targ}-{trans}-{group}")
        train, test = respondent_disjoint_split(rows, keys, seed=10)
        self.assertFalse(set(keys[i] for i in train) & set(keys[i] for i in test))
        self.assertEqual(set(range(len(rows))), set(train) | set(test))
        self.assertEqual(4, len({(rows[i]["Targ"], rows[i]["Trans"]) for i in test}))
        with self.assertRaises(EligibilityError):
            respondent_disjoint_split([{"Targ": 0, "Trans": 0}, {"Targ": 1, "Trans": 0}],
                                      ["synthetic-same", "synthetic-same"])
        with self.assertRaises(EligibilityError):
            respondent_disjoint_split([], [])

    def test_git_ignore_and_staging_guard_cover_restricted_exports(self):
        restricted = "phase10_research/private_data/study1_data.xlsx"
        self.assertTrue(restricted_path(restricted))
        self.assertTrue(restricted_path("phase10_research/derived_data/minimized.csv"))
        self.assertFalse(restricted_path("phase10_research/intake.py"))
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", restricted],
            cwd=ROOT, check=False,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual([], staged_restricted_paths())


if __name__ == "__main__":
    unittest.main()
