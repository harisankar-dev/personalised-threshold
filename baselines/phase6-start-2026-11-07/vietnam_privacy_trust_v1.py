"""Separate descriptive analysis of a secondary Vietnam privacy/trust survey.

No advertising-intrusion target, exposure treatment, or observed transaction
exists in this questionnaire. Associations are not causal or deployable scores.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from survey_phase_v1 import cronbach_alpha


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "secondary_data/user_supplied_2026-11-07/extracted/vietnam_privacy/Dataset of Concerns for Privacy Information Practices and Consumer Behavior in Online Market A survey in Vietnam/Dataset of Concerns for Privacy Information Practices and Consumer Behavior in Online Market_A survey in Vietnam.csv"
RESULT = ROOT / "results/vietnam_privacy_trust_v1.json"
EXPECTED_SHA256 = "3c49ec6134f03f7c08cc89129c9aecd8baba5e300dbfda18bf1b4cc5e169aa8a"
SCALES = {
    "collection_concern": [f"COL{i}" for i in range(1, 5)],
    "accuracy_concern": [f"ERR{i}" for i in range(1, 5)],
    "secondary_use_concern": [f"USU{i}" for i in range(1, 5)],
    "improper_access_concern": [f"IMA{i}" for i in range(1, 4)],
    "online_trust": [f"OT{i}" for i in range(1, 5)],
    "purchase_intention": [f"IB{i}" for i in range(1, 5)],
}
PREDECLARED_PAIRS = [
    ("collection_concern", "online_trust"),
    ("secondary_use_concern", "online_trust"),
    ("online_trust", "purchase_intention"),
    ("collection_concern", "purchase_intention"),
]


def prepare() -> pd.DataFrame:
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Vietnam survey source checksum changed")
    raw = pd.read_csv(SOURCE, encoding="utf-8-sig")
    if raw.shape != (467, 32) or raw.isna().any().any():
        raise ValueError("Unexpected Vietnam survey shape or missing values")
    if any(set(raw[col]) != {1} for col in ("q1", "q2", "q3")):
        raise ValueError("Published screening pattern changed")
    if raw["No"].duplicated().any() or raw.duplicated().any():
        raise ValueError("Duplicate identifier or full response")
    out = raw[["age", "gender", "occupation", "q4"]].copy()
    for name, columns in SCALES.items():
        if not raw[columns].isin(range(1, 6)).all().all():
            raise ValueError(f"Out-of-range scale item: {name}")
        out[name] = raw[columns].mean(axis=1)
    return out


def spearman(x: pd.Series, y: pd.Series) -> float:
    # Pearson correlation of average ranks is Spearman rho; this also handles ties.
    return float(x.rank(method="average").corr(y.rank(method="average")))


def bootstrap_interval(x: pd.Series, y: pd.Series, seed: int, reps: int = 2000) -> list[float]:
    a, b = x.to_numpy(), y.to_numpy()
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(reps):
        sample = rng.integers(0, len(a), len(a))
        values.append(spearman(pd.Series(a[sample]), pd.Series(b[sample])))
    return np.quantile(values, [.025, .975]).tolist()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("Versioned Vietnam analysis already exists")
    data = prepare()
    raw = pd.read_csv(SOURCE, encoding="utf-8-sig")
    scales = {name: {"items": columns,
                     "mean": float(data[name].mean()),
                     "sd": float(data[name].std(ddof=1)),
                     "cronbach_alpha": cronbach_alpha(raw[columns])}
              for name, columns in SCALES.items()}
    associations = {}
    for i, (left, right) in enumerate(PREDECLARED_PAIRS):
        associations[f"{left}_vs_{right}"] = {
            "spearman_rho": spearman(data[left], data[right]),
            "row_bootstrap_95pct_interval": bootstrap_interval(data[left], data[right], 5070 + i),
        }
    age_groups = {str(age): {"n": int((data.age == age).sum()),
                              "trust_purchase_spearman": spearman(data.loc[data.age == age, "online_trust"],
                                                                  data.loc[data.age == age, "purchase_intention"])}
                  for age in sorted(data.age.unique())}
    output = {
        "version": "vietnam_privacy_trust_v1",
        "source": "https://data.mendeley.com/datasets/2x8xnfbsfd/2",
        "source_sha256": EXPECTED_SHA256,
        "license": "CC BY 4.0 (publisher record)",
        "respondents": len(data), "scale_anchors": "1 strongly disagree to 5 strongly agree",
        "scales": scales, "predeclared_descriptive_associations": associations,
        "age_code_subgroups": age_groups,
        "screening_items_q1_q2_q3": "all 467 responses are code 1 (yes); no variation for population prevalence estimates",
        "excluded_fields": {
            "No": "sequential record number, not a predictor",
            "q1_q2_q3": "screening responses all yes",
            "q5": "questionnaire says select all that apply, but CSV stores one code per respondent; multi-response meaning is not recoverable",
        },
        "limits": [
            "Online-store privacy, trust and stated purchase intention; no ad exposure or direct intrusiveness item.",
            "Cross-sectional self-report associations cannot establish direction or causality.",
            "Screening selects only online purchasers affected by improper information use who say they care about privacy.",
            "Bootstrap intervals resample the supplied respondents and do not correct non-probability sampling or common-method bias.",
            "No train/test model was fitted because this dataset does not provide the project's target or a defensible deployment decision.",
        ],
    }
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"respondents": len(data), "associations": associations,
                      "age_subgroups": age_groups}, indent=2))


if __name__ == "__main__":
    main()
