"""Phase 3 audit of respondent intrusion prediction; independent of the 49-C app.

V1 artifacts are read for a fixed-holdout comparison and never overwritten.
Candidate selection uses grouped cross-validation on V1's training partition only.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from survey_phase_v1 import (ROOT, SAV, SEED, INTRUSION, PRIVACY, BENEFITS,
                             AVOIDANCE, read_sav, sha256, cronbach_alpha,
                             fit_ridge, predict_ridge, regression_metrics)


RESULT = ROOT / "results/survey_phase_v2.json"
MODEL = ROOT / "models/unsolicited_intrusiveness_respondent_v2.npz"
V1_RESULT = ROOT / "results/survey_phase_v1.json"
V1_MODEL = ROOT / "models/unsolicited_intrusiveness_respondent_v1.npz"
ALPHAS = (0.1, 1.0, 10.0, 100.0)
BASE = ["Age", "Gender", "Frequency"]
FEATURE_SETS = {
    "A_demographics_social_use": BASE,
    "B_plus_ad_benefits": BASE + ["benefits_mean"],
    "C_plus_privacy": BASE + ["benefits_mean", "privacy_mean"],
    "C_without_explicit_discomfort_items": BASE + ["benefits_mean", "privacy_reduced_mean"],
}
CANDIDATES = {
    "linear_all": FEATURE_SETS["C_plus_privacy"],
    "quadratic_privacy": FEATURE_SETS["C_plus_privacy"] + ["privacy_distance_squared"],
    "linear_reduced_privacy": FEATURE_SETS["C_without_explicit_discomfort_items"],
    "linear_without_privacy": FEATURE_SETS["B_plus_ad_benefits"],
}


def prepare() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    df = read_sav(SAV)
    originals = list(df.columns)
    df = df.copy()
    df["benefits_mean"] = df[BENEFITS].mean(axis=1)
    df["privacy_mean"] = df[PRIVACY].mean(axis=1)
    # PC1 uses "uncomfortable" and PC3 names unwanted advertising.
    # The other privacy questions are still contemporaneous self-reports.
    df["privacy_reduced_mean"] = df[["PC2", "PC4", "PC5", "PC6"]].mean(axis=1)
    df["privacy_distance_squared"] = (df["privacy_mean"] - 4.0) ** 2
    df["intrusion_mean"] = df[INTRUSION].mean(axis=1)
    if not np.allclose(df["intrusion_mean"], df["ITV_mean"]):
        raise ValueError("Intrusion target does not match the source composite")
    groups, _ = pd.factorize(pd.MultiIndex.from_frame(df[originals]))
    return df, df["intrusion_mean"].to_numpy(dtype=float), groups


def grouped_split(groups: np.ndarray, seed: int, training_fraction: float = .8) -> tuple[np.ndarray, np.ndarray]:
    unique = np.unique(groups)
    train_groups = np.random.default_rng(seed).permutation(unique)[:round(training_fraction * len(unique))]
    train_mask = np.isin(groups, train_groups)
    return np.flatnonzero(train_mask), np.flatnonzero(~train_mask)


def forecast(df: pd.DataFrame, y: np.ndarray, train: np.ndarray, test: np.ndarray,
             columns: list[str], alpha: float) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    x = df[columns].to_numpy(dtype=float)
    fit = fit_ridge(x[train], y[train], alpha=alpha)
    return predict_ridge(x[test], fit), fit


def grouped_cv(df: pd.DataFrame, y: np.ndarray, groups: np.ndarray,
               train_idx: np.ndarray) -> list[dict]:
    unique_train_groups = np.unique(groups[train_idx])
    folds = np.array_split(np.random.default_rng(4903).permutation(unique_train_groups), 5)
    rows = []
    for name, columns in CANDIDATES.items():
        for alpha in ALPHAS:
            errors = []
            fold_details = []
            for fold_groups in folds:
                is_valid = np.isin(groups[train_idx], fold_groups)
                inner_train, valid = train_idx[~is_valid], train_idx[is_valid]
                pred, _ = forecast(df, y, inner_train, valid, columns, alpha)
                error = np.abs(pred - y[valid])
                errors.extend(error.tolist())
                fold_details.append({"n": len(valid), "mae": float(error.mean())})
            rows.append({"candidate": name, "alpha": alpha,
                         "out_of_fold_mae": float(np.mean(errors)), "folds": fold_details})
    return rows


def segments(y: np.ndarray, prediction: np.ndarray) -> dict:
    # These are diagnostic summaries of the original seven-point agreement
    # scale, never training labels or calibrated app tiers.
    masks = {
        "below_neutral_mean_lt_4": y < 4,
        "near_neutral_4_to_lt_5": (y >= 4) & (y < 5),
        "agreement_mean_ge_5": y >= 5,
    }
    return {name: {"n": int(mask.sum()), "mae": float(np.mean(np.abs(prediction[mask] - y[mask]))),
                   "mean_error_prediction_minus_observed": float(np.mean(prediction[mask] - y[mask]))}
            for name, mask in masks.items()}


def subgroup(df: pd.DataFrame, y: np.ndarray, pred: np.ndarray, idx: np.ndarray) -> dict:
    age = df.iloc[idx]["Age"].to_numpy()
    gender = df.iloc[idx]["Gender"].to_numpy()
    frequency = df.iloc[idx]["Frequency"].to_numpy()
    masks = {
        "age_19_29": age < 30,
        "age_30_44": (age >= 30) & (age < 45),
        "age_45_plus": age >= 45,
        "gender_code_1": gender == 1,
        "gender_code_2": gender == 2,
        "daily_social_media": frequency == 1,
        "less_than_daily": frequency != 1,
    }
    return {name: {"n": int(mask.sum()),
                   "mae": float(np.mean(np.abs(pred[mask] - y[mask]))) if mask.sum() >= 15 else None,
                   "mean_error_prediction_minus_observed": float(np.mean(pred[mask] - y[mask])) if mask.sum() >= 15 else None}
            for name, mask in masks.items()}


def construct_overlap(df: pd.DataFrame) -> dict:
    corr = df[PRIVACY + INTRUSION].corr()
    cross = np.abs(corr.loc[PRIVACY, INTRUSION].to_numpy()).mean()
    pc_within = np.mean([abs(corr.loc[a, b]) for a, b in combinations(PRIVACY, 2)])
    i_within = np.mean([abs(corr.loc[a, b]) for a, b in combinations(INTRUSION, 2)])
    target = df["intrusion_mean"]
    return {
        "pearson_composite_privacy_intrusion": float(df["privacy_mean"].corr(target)),
        "spearman_composite_privacy_intrusion": float(df["privacy_mean"].rank().corr(target.rank())),
        "privacy_item_pearson_with_intrusion_mean": {c: float(df[c].corr(target)) for c in PRIVACY},
        "htmt_abs_pearson_privacy_intrusion": float(cross / np.sqrt(pc_within * i_within)),
        "cronbach_alpha": {"intrusion": cronbach_alpha(df[INTRUSION]),
                           "privacy": cronbach_alpha(df[PRIVACY]),
                           "benefits": cronbach_alpha(df[BENEFITS])},
        "note": "HTMT and alpha assess item association/internal consistency; they do not establish independent constructs, causality, or predictive validity across populations.",
    }


def false_reassurance(y: np.ndarray, pred: np.ndarray) -> dict:
    high = y >= 5
    return {"high_n": int(high.sum()),
            "high_predicted_below_neutral_4": int(np.sum(high & (pred < 4))),
            "high_predicted_below_agreement_5": int(np.sum(high & (pred < 5))),
            "severe_high_mean_ge_6_predicted_below_neutral_4": int(np.sum((y >= 6) & (pred < 4)))}


def main() -> None:
    if RESULT.exists() or MODEL.exists():
        raise FileExistsError("V2 artifacts already exist; preserve them before a deliberate rerun")
    v1_result = json.loads(V1_RESULT.read_text(encoding="utf-8"))["respondent_survey"]
    if sha256(SAV) != v1_result["sha256"]:
        raise ValueError("Survey source differs from V1")
    df, y, groups = prepare()
    train, test = grouped_split(groups, SEED)
    if (len(train), len(test)) != (v1_result["train_rows"], v1_result["test_rows"]):
        raise ValueError("V1 split was not reproduced")
    baseline = np.full(len(test), y[train].mean())
    with np.load(V1_MODEL) as v1_model:
        x_v1 = df[v1_model["features"].tolist()].to_numpy(dtype=float)
        v1_pred = predict_ridge(x_v1[test],
                                (v1_model["beta"], v1_model["mean"], v1_model["std"]))
    if not np.isclose(regression_metrics(y[test], v1_pred)["mae"],
                      v1_result["holdout_metrics"]["predeclared_combined"]["mae"], atol=1e-12):
        raise ValueError("V1 model artifact and reported MAE disagree")
    fixed_ablation = {}
    fixed_forecasts = {}
    for name, columns in FEATURE_SETS.items():
        pred, _ = forecast(df, y, train, test, columns, 10.0)
        fixed_ablation[name] = regression_metrics(y[test], pred)
        fixed_forecasts[name] = pred
    cv = grouped_cv(df, y, groups, train)
    selected = min(cv, key=lambda row: row["out_of_fold_mae"])
    selected_columns = CANDIDATES[selected["candidate"]]
    v2_pred, fit = forecast(df, y, train, test, selected_columns, selected["alpha"])
    rng = np.random.default_rng(4904)
    boot_baseline_gain, boot_v1_gain, boot_high_gain = [], [], []
    high_idx = np.flatnonzero(y[test] >= 5)
    for _ in range(2000):
        pick = rng.integers(0, len(test), len(test))
        boot_baseline_gain.append(float(np.mean(np.abs(y[test][pick] - baseline[pick]))
                                        - np.mean(np.abs(y[test][pick] - v2_pred[pick]))))
        boot_v1_gain.append(float(np.mean(np.abs(y[test][pick] - v1_pred[pick]))
                                  - np.mean(np.abs(y[test][pick] - v2_pred[pick]))))
        hp = high_idx[rng.integers(0, len(high_idx), len(high_idx))]
        boot_high_gain.append(float(np.mean(np.abs(y[test][hp] - v1_pred[hp]))
                                    - np.mean(np.abs(y[test][hp] - v2_pred[hp]))))
    repeated = []
    for seed in range(100, 130):
        tr, te = grouped_split(groups, seed)
        v1_repeat, _ = forecast(df, y, tr, te, FEATURE_SETS["C_plus_privacy"], 10.0)
        v2_repeat, _ = forecast(df, y, tr, te, selected_columns, selected["alpha"])
        b_repeat, _ = forecast(df, y, tr, te, FEATURE_SETS["B_plus_ad_benefits"], 10.0)
        repeated.append({"seed": seed, "v1_mae": regression_metrics(y[te], v1_repeat)["mae"],
                         "v2_mae": regression_metrics(y[te], v2_repeat)["mae"],
                         "privacy_block_mae_gain": float(np.mean(np.abs(y[te] - b_repeat))
                                                         - np.mean(np.abs(y[te] - v1_repeat)))})
    residual = v2_pred - y[test]
    output = {
        "version": "survey_phase_v2", "source_file": str(SAV.relative_to(ROOT)),
        "source_sha256": sha256(SAV), "respondents": len(df),
        "split": "exact V1 answer-vector-grouped 670/167 split, seed 49",
        "target": "mean of six direct intrusiveness agreement items, original 1-7 scale",
        "diagnostic_segments": "low <4, moderate 4 to <5, high >=5 on respondent item mean; analysis only, not app classes",
        "construct_overlap": construct_overlap(df),
        "feature_sets": FEATURE_SETS,
        "fixed_alpha_10_holdout_ablation": fixed_ablation,
        "training_only_grouped_5_fold_cv": cv,
        "selected_by_training_cv_only": selected,
        "selected_features": selected_columns,
        "holdout_metrics": {
            "training_mean_baseline": regression_metrics(y[test], baseline),
            "v1_saved_model": regression_metrics(y[test], v1_pred),
            "v2_cv_selected": regression_metrics(y[test], v2_pred),
        },
        "holdout_segment_errors": {"v1": segments(y[test], v1_pred),
                                   "v2": segments(y[test], v2_pred)},
        "holdout_subgroups_v2": subgroup(df, y[test], v2_pred, test),
        "false_reassurance": {"v1": false_reassurance(y[test], v1_pred),
                              "v2": false_reassurance(y[test], v2_pred)},
        "v2_residual_quantiles_0_10_25_50_75_90_100": np.quantile(residual, [0, .1, .25, .5, .75, .9, 1]).tolist(),
        "v2_prediction_range": [float(v2_pred.min()), float(v2_pred.max())],
        "holdout_bootstrap_seed": 4904,
        "holdout_bootstrap_replicates": 2000,
        "mae_gain_v2_over_baseline_95pct_interval": np.quantile(boot_baseline_gain, [.025, .975]).tolist(),
        "mae_gain_v2_over_v1_95pct_interval": np.quantile(boot_v1_gain, [.025, .975]).tolist(),
        "high_segment_mae_gain_v2_over_v1_95pct_interval": np.quantile(boot_high_gain, [.025, .975]).tolist(),
        "split_sensitivity": {
            "seeds": "100-129; algorithm fixed from original training CV; not external validation",
            "repeats": repeated,
            "v1_mae_median_and_10_90pct": [float(np.median([x["v1_mae"] for x in repeated])),
                                           *np.quantile([x["v1_mae"] for x in repeated], [.1, .9]).tolist()],
            "v2_mae_median_and_10_90pct": [float(np.median([x["v2_mae"] for x in repeated])),
                                           *np.quantile([x["v2_mae"] for x in repeated], [.1, .9]).tolist()],
            "privacy_block_gain_median_and_10_90pct": [float(np.median([x["privacy_block_mae_gain"] for x in repeated])),
                                                        *np.quantile([x["privacy_block_mae_gain"] for x in repeated], [.1, .9]).tolist()],
        },
        "limits": [
            "One contemporaneous questionnaire per respondent; privacy and intrusion wording overlaps.",
            "No rated ad creatives, randomized levels 0-4, consent conditions, or linked engagement outcomes.",
            "Low-intrusion holdout segment is too small for reliable individual reassurance claims.",
            "Repeated splits and row bootstrap use the same survey, not external validation.",
            "Model cannot accept marketer ad text/images and is not connected to the app.",
        ],
    }
    MODEL.parent.mkdir(exist_ok=True)
    beta, mean, std = fit
    np.savez_compressed(MODEL, beta=beta, mean=mean, std=std,
                        features=np.array(selected_columns), alpha=selected["alpha"],
                        candidate=selected["candidate"], source_sha256=sha256(SAV), seed=SEED)
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"selected": selected, "holdout": output["holdout_metrics"],
                      "segments": output["holdout_segment_errors"],
                      "false_reassurance": output["false_reassurance"]}, indent=2))


if __name__ == "__main__":
    main()
