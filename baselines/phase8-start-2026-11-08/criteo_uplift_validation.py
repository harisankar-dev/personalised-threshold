"""Uncertainty checks for the held-out, feature-group Criteo uplift ranking."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from criteo_visit_uplift import FEATURES, SEED, predict


ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "secondary_data/criteo-uplift/criteo_sample_200k.csv"
MODEL = ROOT / "models/criteo_visit_uplift_v3.npz"
RESULT = ROOT / "results/criteo_uplift_validation_v3.json"


def ranking_gain(outcome: np.ndarray, treatment: np.ndarray, score: np.ndarray) -> tuple[float, float]:
    order = np.argsort(-score, kind="stable")
    y, t = outcome[order], treatment[order]
    treated_n = np.cumsum(t)
    control_n = np.cumsum(1 - t)
    treated_visits = np.cumsum(y * t)
    control_visits = np.cumsum(y * (1 - t))
    cutoffs = np.rint(np.arange(.1, 1.01, .1) * len(y)).astype(int) - 1
    if np.any(treated_n[cutoffs] == 0) or np.any(control_n[cutoffs] == 0):
        raise ValueError("Evaluation slice lacks a treatment arm")
    differences = (treated_visits[cutoffs] / treated_n[cutoffs]
                   - control_visits[cutoffs] / control_n[cutoffs])
    x = np.r_[0.0, np.arange(.1, 1.01, .1)]
    area = np.trapezoid(np.r_[0.0, x[1:] * differences], x)
    random_area = .5 * differences[-1]
    return float(area - random_area), float(differences[0])


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("Validation result already exists")
    df = pd.read_csv(SAMPLE)
    groups, unique_groups = pd.factorize(pd.MultiIndex.from_frame(df[FEATURES]))
    train_group_ids = np.random.default_rng(SEED).permutation(len(unique_groups))[:round(.8 * len(unique_groups))]
    test_idx = np.flatnonzero(~np.isin(groups, train_group_ids))
    raw = df.iloc[test_idx][FEATURES].to_numpy(dtype=np.float64)
    with np.load(MODEL) as model:
        x = np.clip((raw - model["mean"]) / model["std"], -8, 8)
        score = predict(x, model["beta_treated"]) - predict(x, model["beta_control"])
    outcome = df.iloc[test_idx]["visit"].to_numpy(dtype=np.int8)
    treatment = df.iloc[test_idx]["treatment"].to_numpy(dtype=np.int8)
    observed_gain, observed_top_decile = ranking_gain(outcome, treatment, score)
    rng = np.random.default_rng(4901)
    bootstrap_gain = []
    bootstrap_top_decile = []
    for _ in range(400):
        pick = rng.integers(0, len(test_idx), len(test_idx))
        gain, top_decile = ranking_gain(outcome[pick], treatment[pick], score[pick])
        bootstrap_gain.append(gain)
        bootstrap_top_decile.append(top_decile)
    random_gains = []
    for _ in range(400):
        random_gains.append(ranking_gain(outcome, treatment, rng.permutation(score))[0])
    output = {
        "split": "held-out exact feature vectors from v3",
        "test_rows": len(test_idx),
        "bootstrap_seed": 4901,
        "bootstrap_replicates": 400,
        "observed_auuc_gain_over_random": observed_gain,
        "row_bootstrap_95pct_interval_auuc_gain": np.quantile(bootstrap_gain, [.025, .975]).tolist(),
        "observed_top_decile_visit_rate_difference": observed_top_decile,
        "row_bootstrap_95pct_interval_top_decile_difference": np.quantile(bootstrap_top_decile, [.025, .975]).tolist(),
        "random_ranking_replicates": 400,
        "random_ranking_gain_95pct_interval": np.quantile(random_gains, [.025, .975]).tolist(),
        "fraction_random_rankings_at_least_observed_gain": float(np.mean(np.array(random_gains) >= observed_gain)),
        "limitations": [
            "Intervals condition on this fitted model and sampled benchmark; they do not cover model selection or publisher subsampling.",
            "Bootstrap resamples rows because the publisher supplies no user or experiment identifier.",
            "A positive ranking gain does not estimate gains for 49C users or personalization levels.",
        ],
    }
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
