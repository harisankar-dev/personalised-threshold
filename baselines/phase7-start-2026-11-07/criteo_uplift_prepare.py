"""Audit Criteo Uplift and draw a fixed uniform row sample.

This dataset is independent of 49C users and ads. The sample supports an
isolated binary ad-treatment benchmark, not the five personalization levels.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "secondary_data/criteo-uplift/criteo-research-uplift-v2.1.csv.gz"
SAMPLE = ROOT / "secondary_data/criteo-uplift/criteo_sample_200k.csv"
AUDIT = ROOT / "results/criteo_source_audit.json"
EXPECTED_SHA256 = "2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc"
EXPECTED_ROWS = 13_979_592
SAMPLE_SIZE = 200_000
SEED = 49
FEATURES = [f"f{i}" for i in range(12)]
COLUMNS = FEATURES + ["treatment", "conversion", "visit", "exposure"]


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Download the Criteo source to {SOURCE}")
    if SAMPLE.exists() or AUDIT.exists():
        raise FileExistsError("Prepared Criteo artifacts already exist; preserve them before another run")
    with SOURCE.open("rb") as source_file:
        digest = hashlib.file_digest(source_file, "sha256").hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Criteo source checksum differs from the publisher's SHA-256")
    selected = np.sort(np.random.default_rng(SEED).choice(EXPECTED_ROWS, SAMPLE_SIZE, replace=False))
    summary = {
        "source": "https://huggingface.co/datasets/criteo/criteo-uplift",
        "license": "CC BY-NC-SA 4.0",
        "sha256": digest,
        "seed": SEED,
        "sampling": "uniform row indices without replacement across the full gzip CSV",
        "sample_size": SAMPLE_SIZE,
        "columns": COLUMNS,
        "rows": 0,
        "missing_by_column": {col: 0 for col in COLUMNS},
        "treatment_visit_conversion_counts": {},
        "exposure_by_treatment": {},
        "limitations": [
            "12 features are anonymized and cannot be interpreted as 49C user traits",
            "treatment is binary ad targeting versus control, not personalization level 0-4",
            "no intrusion, consent, ad creative, or join key to 49C",
            "publisher reports non-uniform subsampling of original trials",
            "exposure is post-assignment and excluded from model predictors",
        ],
    }
    start = 0
    first = True
    for chunk in pd.read_csv(SOURCE, chunksize=200_000):
        if list(chunk.columns) != COLUMNS:
            raise ValueError("Unexpected Criteo columns")
        stop = start + len(chunk)
        summary["rows"] += len(chunk)
        for col, count in chunk.isna().sum().items():
            summary["missing_by_column"][col] += int(count)
        for (t, v, c), n in chunk.groupby(["treatment", "visit", "conversion"]).size().items():
            key = f"t{int(t)}_v{int(v)}_c{int(c)}"
            summary["treatment_visit_conversion_counts"][key] = summary["treatment_visit_conversion_counts"].get(key, 0) + int(n)
        for (t, e), n in chunk.groupby(["treatment", "exposure"]).size().items():
            key = f"t{int(t)}_e{int(e)}"
            summary["exposure_by_treatment"][key] = summary["exposure_by_treatment"].get(key, 0) + int(n)
        left, right = np.searchsorted(selected, [start, stop])
        if right > left:
            picked = chunk.iloc[selected[left:right] - start]
            picked.to_csv(SAMPLE, mode="w" if first else "a", header=first, index=False)
            first = False
        start = stop
    if summary["rows"] != EXPECTED_ROWS or first:
        raise ValueError(f"Unexpected source row count or empty sample: {summary['rows']}")
    AUDIT.parent.mkdir(exist_ok=True)
    AUDIT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"rows": summary["rows"], "sample_size": SAMPLE_SIZE,
                      "missing_total": sum(summary["missing_by_column"].values()),
                      "counts": summary["treatment_visit_conversion_counts"]}, indent=2))


if __name__ == "__main__":
    main()
