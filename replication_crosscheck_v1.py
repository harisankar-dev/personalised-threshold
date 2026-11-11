"""Audit OSF replication scripts, pooled workbook, and field aggregates.

Respondent IDs are used only for an in-memory equality check. Output contains
aggregate counts and checksums, never IDs or participant-level values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from location_condition_research_v1 import FILES


POOLED = ("supplemental_analysis_study1_study2/01_data/study1_2.xlsx",
          "982fad7669b0ca0afec94efae2dfc7a86661545c3d1803a5a662ec29a7b3dea0")
FIELD = ("study_3/01_data/study3_data.xlsx",
         "7e9886b90bb2ffa8ad8dde5127e3af9aab94cd54fec7dc7d8ab6037915c232d5")
SCRIPTS = {
    "study_1/02_code/study1_replication.R": 'y="ITC"',
    "study_2/02_code/study2_replication.R": 'y="ITC"',
    "study_3/02_code/study3_replication.R": "chisq.test",
    "supplemental_analysis_study1_study2/02_code/suppl_analysis_12.R": "lm(PP ~ Pers",
}
AUDIT_COLUMNS = ["ResponseId", "Targ", "Trans", "PP", "PPI", "PPR", "ITC"] + [f"PPI_{i}" for i in range(1, 10)]


def checked_path(root: Path, relative: str, expected: str) -> Path:
    path = root / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Changed input: {path.name}")
    return path


def audit(root: Path) -> dict:
    source = []
    for study, (relative, expected) in enumerate(FILES.values(), start=1):
        frame = pd.read_excel(checked_path(root, relative, expected), usecols=AUDIT_COLUMNS)
        if frame.ResponseId.isna().any() or frame.ResponseId.duplicated().any():
            raise ValueError(f"Invalid respondent keys in Study {study}")
        frame["study"] = study
        source.append(frame)
    original = pd.concat(source, ignore_index=True)
    pooled = pd.read_excel(checked_path(root, *POOLED),
                           usecols=["ResponseId", "NoPers", "LowSpec", "HighSpec", "Pers",
                                    "Trans", "PP", "PPI", "PPR", "ITC"] + [f"PPI_{i}" for i in range(1, 10)])
    if pooled.ResponseId.isna().any() or pooled.ResponseId.duplicated().any():
        raise ValueError("Invalid pooled respondent keys")
    if set(original.ResponseId) != set(pooled.ResponseId):
        raise ValueError("Pooled workbook is not the same respondent set")
    onehot = pooled[["NoPers", "LowSpec", "HighSpec"]]
    if not onehot.isin((0, 1)).all().all() or not (onehot.sum(axis=1) == 1).all():
        raise ValueError("Invalid pooled personalization coding")
    if not (pooled.Pers.to_numpy() == onehot.to_numpy().argmax(axis=1) + 1).all():
        raise ValueError("Pooled Pers does not match the one-hot columns")
    matched = original.merge(pooled, on="ResponseId", suffixes=("_source", "_pool"), validate="one_to_one")
    mismatch = {}
    for column in ["Trans", "PP", "PPI", "PPR", "ITC"] + [f"PPI_{i}" for i in range(1, 10)]:
        mismatch[column] = int(((matched[f"{column}_source"] - matched[f"{column}_pool"]).abs() > 1e-7).sum())
    changed = (matched.PPI_source - matched.PPI_pool).abs() > 1e-7
    mismatch_cells = matched.loc[changed].groupby(["study", "Targ", "Trans_source"]).size()
    mapping = matched.groupby(["study", "Targ", "Pers"]).size()
    field = pd.read_excel(checked_path(root, *FIELD), usecols=["Ad set name", "Clicks", "Reach", "Impressions"])
    if len(field) != 4 or field["Ad set name"].duplicated().any():
        raise ValueError("Unexpected field ad sets")
    scripts = {}
    for relative, expected_fragment in SCRIPTS.items():
        path = root / relative
        content = path.read_bytes()
        if expected_fragment not in content.decode("utf-8-sig", errors="replace"):
            raise ValueError(f"Replication script changed role: {path.name}")
        scripts[relative] = hashlib.sha256(content).hexdigest()
    return {
        "pooled_source_sha256": POOLED[1],
        "pooled_rows": len(pooled),
        "same_respondent_ids_as_studies_1_and_2": True,
        "one_hot_and_pers_consistent_rows": len(pooled),
        "study_target_to_pers_counts": [
            {"study": int(s), "targeting_code": int(t), "pers_code": int(p), "n": int(n)}
            for (s, t, p), n in mapping.items()
        ],
        "column_mismatch_counts_by_respondent_id": mismatch,
        "ppi_mismatch_cells": [
            {"study": int(s), "targeting_code": int(t), "disclosure_code": int(d), "n": int(n)}
            for (s, t, d), n in mismatch_cells.items()
        ],
        "field_source_sha256": FIELD[1],
        "field_aggregate_ad_sets": [
            {"condition": str(row["Ad set name"]), "clicks": int(row.Clicks),
             "reach": int(row.Reach), "impressions": int(row.Impressions),
             "clicks_per_reach": float(row.Clicks / row.Reach)}
            for _, row in field.iterrows()
        ],
        "script_sha256": scripts,
        "interpretation": (
            f"Pooled rows are not independent; {mismatch['PPI']} PPI composite values differ. "
            "Field clicks are aggregate events, not linked privacy responses."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; use a new versioned path")
    result = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote aggregate replication audit: {args.output}")


if __name__ == "__main__":
    main()
