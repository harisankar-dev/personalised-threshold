"""Read-only-on-existing-artifacts replay of 49-C research experiments.

Every replay writes only inside a temporary workspace directory. Existing
models, source data, reports, and result files are never replaced.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "results/phase5_repro_audit.json"


def equivalent(actual: object, expected: object, where: str = "result") -> None:
    """Compare deterministic structures with only floating-point roundoff tolerance."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or actual.keys() != expected.keys():
            raise AssertionError(f"Different keys at {where}")
        for key in expected:
            equivalent(actual[key], expected[key], f"{where}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError(f"Different list at {where}")
        for i, (got, want) in enumerate(zip(actual, expected)):
            equivalent(got, want, f"{where}[{i}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if not isinstance(actual, (int, float)) or not np.isclose(actual, expected, rtol=1e-11, atol=1e-12):
            raise AssertionError(f"Different number at {where}: {actual} != {expected}")
    elif actual != expected:
        raise AssertionError(f"Different value at {where}: {actual} != {expected}")


def compare_models(actual_path: Path, expected_path: Path) -> None:
    with np.load(actual_path, allow_pickle=False) as got, np.load(expected_path, allow_pickle=False) as want:
        if set(got.files) != set(want.files):
            raise AssertionError("Model artifact fields differ")
        for key in want.files:
            if np.issubdtype(want[key].dtype, np.number):
                np.testing.assert_allclose(got[key], want[key], rtol=1e-11, atol=1e-12)
            else:
                np.testing.assert_array_equal(got[key], want[key])


def compare_results(actual_path: Path, expected_path: Path) -> None:
    equivalent(json.loads(actual_path.read_text(encoding="utf-8")),
               json.loads(expected_path.read_text(encoding="utf-8")))


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("Phase 5 audit result exists; preserve it before deliberate rerun")
    checkpoint = ROOT / "baselines/phase5-start-2026-11-06/sha256.json"
    manifest = json.loads(checkpoint.read_text(encoding="utf-8"))
    original_hashes = {rel: sha256(ROOT / rel) == digest for rel, digest in manifest.items()}
    allowed_documentation_edits = {"CHANGELOG.md", "PROJECT_STATUS.md", "web/index.html"}
    unexpected_changes = [rel for rel, equal in original_hashes.items()
                          if not equal and rel not in allowed_documentation_edits]
    if unexpected_changes:
        raise AssertionError(f"Unexpected changes to checkpointed files: {unexpected_changes}")
    verified = {}
    with tempfile.TemporaryDirectory(prefix="phase5-replay-", dir=ROOT) as temp:
        temporary = Path(temp)

        import survey_phase_v1 as s1
        respondent, fit = s1.respondent_survey()
        genz = s1.genz_survey()
        saved = json.loads(s1.RESULT.read_text(encoding="utf-8"))
        equivalent(respondent, saved["respondent_survey"])
        equivalent(genz, saved["genz_survey"])
        with np.load(s1.MODEL, allow_pickle=False) as model:
            for key, arr in zip(("beta", "mean", "std"), fit):
                np.testing.assert_allclose(arr, model[key], rtol=1e-11, atol=1e-12)
        verified["survey_v1"] = "source, metrics, coefficients and Gen Z audit reproduced"

        import survey_phase_v2 as s2
        old_result, old_model = s2.RESULT, s2.MODEL
        try:
            s2.RESULT = temporary / "survey_v2.json"
            s2.MODEL = temporary / "survey_v2.npz"
            with contextlib.redirect_stdout(io.StringIO()):
                s2.main()
            compare_results(s2.RESULT, old_result)
            compare_models(s2.MODEL, old_model)
        finally:
            s2.RESULT, s2.MODEL = old_result, old_model
        verified["survey_v2"] = "selection, metrics and model arrays reproduced"

        import survey_phase_v3_uncertainty as s3
        old_result, old_model = s3.RESULT, s3.MODEL
        try:
            s3.RESULT = temporary / "survey_v3.json"
            s3.MODEL = temporary / "survey_v3.npz"
            with contextlib.redirect_stdout(io.StringIO()):
                s3.main()
            compare_results(s3.RESULT, old_result)
            compare_models(s3.MODEL, old_model)
        finally:
            s3.RESULT, s3.MODEL = old_result, old_model
        verified["survey_v3_uncertainty"] = "fit/calibration split, coverage and model arrays reproduced"

        import ad_blockers_intrusion_v1 as ext
        old_result, old_model = ext.RESULT, ext.MODEL
        try:
            ext.RESULT = temporary / "external.json"
            ext.MODEL = temporary / "external.npz"
            with contextlib.redirect_stdout(io.StringIO()):
                ext.main()
            compare_results(ext.RESULT, old_result)
            compare_models(ext.MODEL, old_model)
        finally:
            ext.RESULT, ext.MODEL = old_result, old_model
        verified["independent_ad_blockers"] = "source, training selection, metrics and model arrays reproduced"

        import criteo_visit_uplift as cri
        old_root, old_argv = cri.ROOT, sys.argv
        try:
            cri.ROOT = temporary
            sys.argv = ["criteo_visit_uplift.py", "--split", "feature-group"]
            with contextlib.redirect_stdout(io.StringIO()):
                cri.main()
            compare_results(temporary / "results/criteo_visit_uplift_v3.json",
                            ROOT / "results/criteo_visit_uplift_v3.json")
            compare_models(temporary / "models/criteo_visit_uplift_v3.npz",
                           ROOT / "models/criteo_visit_uplift_v3.npz")
        finally:
            cri.ROOT, sys.argv = old_root, old_argv
        verified["criteo_visit_v3"] = "grouped split, arm metrics and model arrays reproduced"

        import criteo_uplift_validation as cv
        old_result = cv.RESULT
        try:
            cv.RESULT = temporary / "criteo_validation.json"
            with contextlib.redirect_stdout(io.StringIO()):
                cv.main()
            compare_results(cv.RESULT, old_result)
        finally:
            cv.RESULT = old_result
        verified["criteo_uplift_validation_v3"] = "ranking and bootstrap outputs reproduced"

        import analysis
        old_out = analysis.OUT
        try:
            analysis.OUT = temporary / "original_analysis"
            analysis.OUT.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                analysis.main()
            for name in ("audit", "baseline", "associations"):
                compare_results(analysis.OUT / f"{name}.json", ROOT / "results" / f"{name}.json")
        finally:
            analysis.OUT = old_out
        verified["original_49c_event_analysis"] = "audit, baseline and associations reproduced"

    output = {
        "version": "phase5_repro_audit",
        "checkpoint_manifest_entries": len(original_hashes),
        "unchanged_checkpoint_entries": sum(original_hashes.values()),
        "expected_copy_and_documentation_edits": [rel for rel, equal in original_hashes.items()
                                                  if not equal and rel in allowed_documentation_edits],
        "experiments": verified,
        "source_hashes": {rel: digest for rel, digest in manifest.items()
                          if rel.startswith("try these dataset/") or rel.startswith("secondary_data/")},
        "limits": ["This replays prior experiment designs; it is not independent external validation.",
                   "Previously examined holdouts remain previously examined even when scores reproduce.",
                   "No five-level personalization treatment or direct linked intrusion/engagement outcome is created."],
    }
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"checkpoint_entries": len(original_hashes),
                      "unchanged_entries": sum(original_hashes.values()), "replayed": verified}, indent=2))


if __name__ == "__main__":
    main()
