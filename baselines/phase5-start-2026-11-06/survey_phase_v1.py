"""Independent secondary-survey audit and respondent-level intrusion experiment.

No survey records are joined to 49-C users or ads. All outputs are versioned.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SAV = ROOT / "try these dataset/Consumer perceptions towards unsolicited ads on social media.sav"
GENZ = ROOT / "try these dataset/GenZ_Personalized_Ads_Purchase_Dataset_N296.xlsx"
RESULT = ROOT / "results/survey_phase_v1.json"
MODEL = ROOT / "models/unsolicited_intrusiveness_respondent_v1.npz"
SEED = 49
RIDGE_ALPHA = 10.0
INTRUSION = [f"I{i}" for i in range(1, 7)]
PRIVACY = [f"PC{i}" for i in range(1, 7)]
BENEFITS = [f"PAB{i}" for i in range(1, 5)]
AVOIDANCE = [f"AAB{i}" for i in range(1, 5)]


def read_sav(path: Path) -> pd.DataFrame:
    try:
        import pyreadstat
    except ModuleNotFoundError:
        sys.path.insert(0, str(ROOT / ".vendor"))
        import pyreadstat
    return pyreadstat.read_sav(str(path), apply_value_formats=False)[0]


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def cronbach_alpha(items: pd.DataFrame) -> float:
    k = items.shape[1]
    return float(k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float = RIDGE_ALPHA) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Training-only scaling and an unpenalized intercept."""
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std == 0] = 1
    design = np.column_stack((np.ones(len(x)), (x - mean) / std))
    penalty = np.diag([0.0] + [alpha] * x.shape[1])
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return beta, mean, std


def predict_ridge(x: np.ndarray, fit: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    beta, mean, std = fit
    return np.clip(beta[0] + ((x - mean) / std) @ beta[1:], 1, 7)


def regression_metrics(y: np.ndarray, forecast: np.ndarray) -> dict:
    error = forecast - y
    return {
        "n": len(y),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "r2_vs_test_mean": float(1 - np.sum(error ** 2) / np.sum((y - y.mean()) ** 2)),
        "mean_error_prediction_minus_observed": float(error.mean()),
    }


def percentile_interval(values: np.ndarray) -> list[float]:
    return np.quantile(values, [.025, .975]).tolist()


def respondent_survey() -> tuple[dict, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    df = read_sav(SAV)
    expected = AVOIDANCE + BENEFITS + PRIVACY + INTRUSION + ["Age", "Gender", "Frequency"]
    if len(df) != 837 or df[expected].isna().any().any():
        raise ValueError("Unexpected respondent count or missing construct values")
    for name, cols in {"avoidance": AVOIDANCE, "benefits": BENEFITS,
                       "privacy": PRIVACY, "intrusiveness": INTRUSION}.items():
        if not df[cols].isin(range(1, 8)).all().all():
            raise ValueError(f"Invalid seven-point response in {name}")
    if not np.allclose(df[INTRUSION].mean(axis=1), df["ITV_mean"]):
        raise ValueError("Published intrusion composite does not equal the six item mean")
    df = df.copy()
    df["intrusion_mean"] = df[INTRUSION].mean(axis=1)
    df["privacy_mean"] = df[PRIVACY].mean(axis=1)
    df["benefits_mean"] = df[BENEFITS].mean(axis=1)
    df["avoidance_mean"] = df[AVOIDANCE].mean(axis=1)
    # Two identical answer vectors are retained as possible distinct respondents.
    # They are assigned to the same partition to avoid exact-answer leakage.
    groups, unique_rows = pd.factorize(pd.MultiIndex.from_frame(df.drop(columns=[
        "intrusion_mean", "privacy_mean", "benefits_mean", "avoidance_mean"])))
    train_groups = np.random.default_rng(SEED).permutation(len(unique_rows))[:round(.8 * len(unique_rows))]
    is_train = np.isin(groups, train_groups)
    train_idx, test_idx = np.flatnonzero(is_train), np.flatnonzero(~is_train)
    y = df["intrusion_mean"].to_numpy(dtype=float)
    feature_sets = {
        "demographics": ["Age", "Gender", "Frequency"],
        "demographics_plus_benefits": ["Age", "Gender", "Frequency", "benefits_mean"],
        "demographics_plus_privacy": ["Age", "Gender", "Frequency", "privacy_mean"],
        "predeclared_combined": ["Age", "Gender", "Frequency", "benefits_mean", "privacy_mean"],
    }
    baseline = np.full(len(test_idx), y[train_idx].mean())
    metrics = {"training_mean_baseline": regression_metrics(y[test_idx], baseline)}
    fits = {}
    forecasts = {}
    for name, columns in feature_sets.items():
        x = df[columns].to_numpy(dtype=float)
        fit = fit_ridge(x[train_idx], y[train_idx])
        forecast = predict_ridge(x[test_idx], fit)
        metrics[name] = regression_metrics(y[test_idx], forecast)
        fits[name], forecasts[name] = fit, forecast
    primary = forecasts["predeclared_combined"]
    rng = np.random.default_rng(4901)
    improvement = []
    for _ in range(1000):
        pick = rng.integers(0, len(test_idx), len(test_idx))
        improvement.append(np.mean(np.abs(y[test_idx][pick] - baseline[pick]))
                           - np.mean(np.abs(y[test_idx][pick] - primary[pick])))
    quintiles = pd.qcut(primary, 5, labels=False, duplicates="drop")
    calibration = [
        {"quintile": int(q) + 1, "n": int(np.sum(quintiles == q)),
         "predicted_mean": float(primary[quintiles == q].mean()),
         "observed_mean": float(y[test_idx][quintiles == q].mean())}
        for q in np.sort(np.unique(quintiles))
    ]
    construct = df[["intrusion_mean", "privacy_mean", "benefits_mean", "avoidance_mean"]]
    report = {
        "source_file": str(SAV.relative_to(ROOT)), "sha256": sha256(SAV),
        "respondents": len(df), "missing_cells": int(df.isna().sum().sum()),
        "exact_duplicate_answer_rows_retained": int(df.duplicated().sum()),
        "split": "seed 49, 80/20 by exact full response vector; no respondent ID exists",
        "train_rows": len(train_idx), "test_rows": len(test_idx),
        "target": "mean of I1-I6 direct 1-7 intrusion agreement items",
        "target_mean": float(y.mean()), "target_sd": float(y.std(ddof=1)),
        "construct_means": construct.mean().to_dict(),
        "cronbach_alpha": {name: cronbach_alpha(df[cols]) for name, cols in {
            "intrusiveness": INTRUSION, "privacy_concern": PRIVACY,
            "perceived_ad_benefits": BENEFITS, "ad_avoidance": AVOIDANCE}.items()},
        "spearman_construct_correlations": construct.corr(method="spearman").to_dict(),
        "feature_sets": feature_sets,
        "excluded_predictors": INTRUSION + ["ITV_mean", "avoidance_mean"] + AVOIDANCE,
        "ridge_alpha": RIDGE_ALPHA,
        "holdout_metrics": metrics,
        "primary_mae_improvement_vs_baseline": float(metrics["training_mean_baseline"]["mae"] - metrics["predeclared_combined"]["mae"]),
        "row_bootstrap_95pct_interval_mae_improvement": percentile_interval(np.array(improvement)),
        "holdout_prediction_quintiles": calibration,
        "limitations": [
            "One general response per person about unsolicited/social-media ads, not ratings of individual creatives.",
            "No observed personalization levels 0-4, consent choices, or intervention assignment.",
            "Privacy items and intrusion items are contemporaneous self-reports with overlapping wording; prediction may reflect shared-method response style.",
            "No respondent identifier exists; exact-answer grouping cannot rule out repeated people.",
            "This respondent profile model cannot score an ad image or copy in the marketer app.",
        ],
    }
    return report, fits["predeclared_combined"]


def genz_survey() -> dict:
    df = pd.read_excel(GENZ)
    if df.shape != (296, 35) or df.isna().any().any():
        raise ValueError("Unexpected Gen Z workbook shape or missing data")
    groups = {
        "perceived_personalization": range(7, 12),
        "usefulness": range(12, 17),
        "relevance": range(17, 22),
        "novelty": range(22, 26),
        "privacy_concern": range(26, 30),
        "purchase_reaction": range(30, 35),
    }
    if not df.iloc[:, 7:35].isin(range(1, 6)).all().all():
        raise ValueError("Unexpected agreement response codes in Gen Z workbook")
    composites = pd.DataFrame({name: df.iloc[:, list(indices)].mean(axis=1)
                               for name, indices in groups.items()})
    correlations = composites.corr(method="spearman")
    rng = np.random.default_rng(4902)
    pair_intervals = {}
    for name in ("perceived_personalization", "relevance", "privacy_concern"):
        values = []
        for _ in range(1000):
            picked = rng.integers(0, len(df), len(df))
            values.append(composites.iloc[picked][[name, "purchase_reaction"]]
                          .corr(method="spearman").iloc[0, 1])
        pair_intervals[name] = {
            "spearman_rho": float(correlations.loc[name, "purchase_reaction"]),
            "row_bootstrap_95pct_interval": percentile_interval(np.array(values)),
        }
    return {
        "source_file": str(GENZ.relative_to(ROOT)), "sha256": sha256(GENZ),
        "respondents": len(df), "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "exact_duplicate_rows_retained": int(df.duplicated().sum()),
        "birth_year_range": [int(df.iloc[:, 1].min()), int(df.iloc[:, 1].max())],
        "construct_column_positions_zero_based": {name: list(indices) for name, indices in groups.items()},
        "construct_means": composites.mean().to_dict(),
        "spearman_correlations": correlations.to_dict(),
        "purchase_reaction_associations": pair_intervals,
        "recent_ad_click_response_code_counts": {str(k): int(v) for k, v in df.iloc[:, 5].value_counts().sort_index().items()},
        "recent_ad_purchase_response_code_counts": {str(k): int(v) for k, v in df.iloc[:, 6].value_counts().sort_index().items()},
        "limits": [
            "Workbook provides item wording but no verified codebook, response anchors, survey date, respondent IDs, or sampling documentation.",
            "Click and purchase response code meanings are unverified, so no click or purchase rate is reported.",
            "The last five items mix purchase intentions, self-reported past purchase, and shopping frequency; their mean is labelled purchase reaction, not observed sales.",
            "All associations are cross-sectional self-reports, not causal effects or ad-level performance.",
            "No direct intrusion items or five-level treatment are present.",
        ],
    }


def main() -> None:
    if RESULT.exists() or MODEL.exists():
        raise FileExistsError("Version 1 survey output exists; preserve it before a deliberate rerun")
    respondent, fit = respondent_survey()
    genz = genz_survey()
    MODEL.parent.mkdir(exist_ok=True)
    beta, mean, std = fit
    np.savez_compressed(MODEL, beta=beta, mean=mean, std=std,
                        features=np.array(respondent["feature_sets"]["predeclared_combined"]),
                        target="I1-I6 respondent mean", source_sha256=respondent["sha256"], seed=SEED)
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps({"version": "survey_phase_v1", "respondent_survey": respondent,
                                  "genz_survey": genz}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"respondent_holdout": respondent["holdout_metrics"],
                      "respondent_mae_improvement_interval": respondent["row_bootstrap_95pct_interval_mae_improvement"],
                      "genz_purchase_associations": genz["purchase_reaction_associations"]}, indent=2))


if __name__ == "__main__":
    main()
