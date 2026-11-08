"""Separate, aggregate-only survey persona audit for Phase 7.

These are transparent descriptive quadrants, not trained clusters or campaign
audience assignments. The script refuses to replace its versioned output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat


ROOT = Path(__file__).resolve().parent
GENZ = ROOT / "try these dataset" / "GenZ_Personalized_Ads_Purchase_Dataset_N296.xlsx"
ROMANO = ROOT / "try these dataset" / "Consumer perceptions towards unsolicited ads on social media.sav"
EXPECTED_HASHES = {
    "genz": "a90b27698b116127c4e0850c77137a348b6201d4fc78241e4ac540012ebf865e",
    "romano_han": "a3b2d6a56d89d163f11150b5e6bf7ec14d54e60998a7f371a099cdeb7dc3a267",
}
LABELS = (
    "higher_value_lower_concern", "higher_value_higher_concern",
    "lower_value_lower_concern", "lower_value_higher_concern",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alpha(items: pd.DataFrame) -> float:
    matrix = items.to_numpy(dtype=float)
    k = matrix.shape[1]
    total = matrix.sum(axis=1)
    return float(k / (k - 1) * (1 - matrix.var(axis=0, ddof=1).sum() / total.var(ddof=1)))


def labels(value: np.ndarray, concern: np.ndarray, cutoff: float) -> np.ndarray:
    return np.array([
        ("higher_value" if v >= cutoff else "lower_value") +
        ("_higher_concern" if c >= cutoff else "_lower_concern")
        for v, c in zip(value, concern)
    ])


def summarize(name: str, value_items: pd.DataFrame, concern_items: pd.DataFrame,
              cutoff: float, *, source: str, extra: dict) -> dict:
    if value_items.isna().any().any() or concern_items.isna().any().any():
        raise ValueError("Scale items contain missing values")
    observed = np.concatenate((value_items.to_numpy(), concern_items.to_numpy()), axis=1)
    maximum = 5 if name == "genz" else 7
    if not np.all(np.isfinite(observed)) or np.any(observed < 1) or np.any(observed > maximum):
        raise ValueError("Scale item outside documented response range")
    value = value_items.mean(axis=1).to_numpy()
    concern = concern_items.mean(axis=1).to_numpy()
    group = labels(value, concern, cutoff)
    n = len(group)
    rng = np.random.default_rng(4907 if name == "genz" else 4908)
    samples = rng.integers(0, n, size=(2000, n))
    counts = {label: int(np.count_nonzero(group == label)) for label in LABELS}
    intervals = {
        label: [round(float(x), 4) for x in np.quantile((group[samples] == label).mean(axis=1), [.025, .975])]
        for label in LABELS
    }
    drop_agreement = []
    for items, other, dropped_value in ((value_items, concern, True), (concern_items, value, False)):
        for column in items:
            reduced = items.drop(columns=column).mean(axis=1).to_numpy()
            revised = labels(reduced, other, cutoff) if dropped_value else labels(other, reduced, cutoff)
            drop_agreement.append(float(np.mean(group == revised)))
    shifted = {}
    for delta in (-.25, .25):
        new_group = labels(value, concern, cutoff + delta)
        shifted[f"{delta:+.2f}"] = {
            "agreement_with_primary_rule": round(float(np.mean(new_group == group)), 4),
            "counts": {label: int(np.count_nonzero(new_group == label)) for label in LABELS},
        }
    return {
        "source_file": source,
        "respondents": n,
        "unit": "one unlinked self-reported survey answer row",
        "value_items": list(value_items.columns),
        "concern_items": list(concern_items.columns),
        "value_mean": round(float(value.mean()), 4),
        "concern_mean": round(float(concern.mean()), 4),
        "value_alpha": round(alpha(value_items), 4),
        "concern_alpha": round(alpha(concern_items), 4),
        "value_concern_spearman": round(float(pd.Series(value).rank().corr(pd.Series(concern).rank())), 4),
        "rule": f"Higher means item-average >= {cutoff}; lower means item-average < {cutoff} on the source scale.",
        "counts": counts,
        "shares": {label: round(count / n, 4) for label, count in counts.items()},
        "respondent_bootstrap_95pct_share_intervals": intervals,
        "leave_one_item_out_assignment_agreement_range": [round(min(drop_agreement), 4), round(max(drop_agreement), 4)],
        "cutoff_sensitivity": shifted,
        **extra,
    }


def analyze() -> dict:
    for name, path in (("genz", GENZ), ("romano_han", ROMANO)):
        if sha256(path) != EXPECTED_HASHES[name]:
            raise ValueError(f"{name} source hash differs from the audited file")
    genz = pd.read_excel(GENZ)
    romano, _ = pyreadstat.read_sav(str(ROMANO))
    if genz.shape != (296, 35) or romano.shape != (837, 27):
        raise ValueError("Survey shape differs from the audited source")
    if not str(genz.columns[17]).startswith("Sosyal medyadaki kişiselleştirilmiş reklamların benimle"):
        raise ValueError("Gen Z relevance item order changed")
    if not str(genz.columns[26]).startswith("Sosyal medyada kişiselleştirilmiş reklamlar gördüğümde gizlilik"):
        raise ValueError("Gen Z privacy item order changed")
    romano_benefit = [f"PAB{i}" for i in range(1, 5)]
    romano_privacy = [f"PC{i}" for i in range(1, 7)]
    result = {
        "version": "phase7_segmentation_v1",
        "method": "Predeclared midpoint-based two-axis survey description; no clustering, treatment inference, cross-source join or operational audience label.",
        "source_sha256": EXPECTED_HASHES,
        "genz": summarize(
            "genz", genz.iloc[:, 17:22], genz.iloc[:, 26:30], 3.5,
            source=str(GENZ.relative_to(ROOT)),
            extra={
                "source_scale": "1 strongly disagree to 5 strongly agree; publisher description",
                "exact_duplicate_full_rows_retained": int(genz.duplicated().sum()),
                "birth_year_2009_or_later": int((genz.iloc[:, 1] >= 2009).sum()),
                "construct": "perceived relevance of personalized social-media ads versus privacy concern",
            },
        ),
        "romano_han": summarize(
            "romano_han", romano[romano_benefit], romano[romano_privacy], 4.5,
            source=str(ROMANO.relative_to(ROOT)),
            extra={
                "source_scale": "1 to 7 agreement responses; source item interpretation in prior survey audit",
                "exact_duplicate_full_rows_retained": int(romano.duplicated().sum()),
                "construct": "perceived benefits of unsolicited social-media ads versus privacy concern",
            },
        ),
        "limitations": [
            "These are descriptive survey quadrants, not empirical classes, optimized clusters, or consented targetable audiences.",
            "Bootstrap intervals describe sampling variability within each convenience source; they do not correct sampling bias.",
            "Item-drop and cutoff sensitivity are rule robustness checks, not external or temporal validation.",
            "Gen Z relevance is not a direct preference for a targeting method or personalization intensity.",
            "Romano benefits refer to unsolicited ads generally; its respondent IDs cannot join Gen Z, UPAD or campaign audiences.",
            "No ad-specific response or segment-level uplift is estimated.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "phase7_segmentation_v1.json")
    args = parser.parse_args()
    result = analyze()
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
    print(f"Saved aggregate-only segmentation audit to {path}")


if __name__ == "__main__":
    main()
