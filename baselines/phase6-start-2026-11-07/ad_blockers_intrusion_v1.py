"""Independent Phase 4 benchmark of general web-ad intrusion responses.

Redondo and Aznar's public CC0 survey does not measure personalization
treatments or responses to uploaded ad creatives. It is never joined to 49-C.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "secondary_data/research_candidates/redondo_aznar_ad_blockers_2018.xlsx"
RESULT = ROOT / "results/ad_blockers_intrusion_v1.json"
MODEL = ROOT / "models/ad_blockers_intrusion_v1.npz"
EXPECTED_SHA256 = "7da6b2c4c178b675ad69339bc6f3e18d7eef52e8e70e87ee7e4a79767c2c439d"
SOURCE_URL = "https://data.mendeley.com/datasets/89nk3kp8tg/1"
SEED = 1049
ALPHAS = (0.1, 1.0, 10.0, 100.0)
FEATURES = {
    "A_demographics": ["Age", "male"],
    "B_plus_other_ad_attitudes": ["Age", "male", "knowledge", "ad_attitude", "pleasure", "credibility", "economic_value"],
    "C_plus_clutter": ["Age", "male", "knowledge", "ad_attitude", "pleasure", "credibility", "economic_value", "ad_clutter"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    if sha256(SOURCE) != EXPECTED_SHA256:
        raise ValueError("External survey checksum differs from the audited download")
    raw = pd.read_excel(SOURCE, sheet_name="Data of ad blockers")
    if raw.shape != (1511, 32) or raw.isna().any().any():
        raise ValueError("Unexpected external survey shape or missingness")
    if set(raw.Sex) != {"male", "female"}:
        raise ValueError("Unexpected sex code")
    items = [c for c in raw if "_" in c and c.rsplit("_", 1)[-1] in {"1", "2", "3", "4"}]
    if raw[items].min().min() < -3 or raw[items].max().max() > 3:
        raise ValueError("Questionnaire responses outside published -3 to +3 anchors")
    df = raw.copy()
    df["male"] = (raw.Sex == "male").astype(float)
    for name, prefix in (("intrusion", "ioa"), ("ad_clutter", "oac"), ("knowledge", "kab"),
                         ("ad_attitude", "aoa"), ("pleasure", "poa"),
                         ("credibility", "coa"), ("economic_value", "eoa")):
        df[name] = raw[[f"{prefix}_{i}" for i in range(1, 5)]].mean(axis=1)
    # Full response vectors distinguish possible participants where no ID exists.
    groups, _ = pd.factorize(pd.MultiIndex.from_frame(raw))
    return df, df.intrusion.to_numpy(dtype=float), groups


def grouped_split(groups: np.ndarray, seed: int = SEED) -> tuple[np.ndarray, np.ndarray]:
    unique = np.unique(groups)
    train_groups = np.random.default_rng(seed).permutation(unique)[:round(.8 * len(unique))]
    mask = np.isin(groups, train_groups)
    return np.flatnonzero(mask), np.flatnonzero(~mask)


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean, std = x.mean(axis=0), x.std(axis=0)
    std[std == 0] = 1
    design = np.column_stack((np.ones(len(x)), (x - mean) / std))
    penalty = np.diag([0] + [alpha] * x.shape[1])
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return beta, mean, std


def predict(x: np.ndarray, fit: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    beta, mean, std = fit
    return np.clip(beta[0] + ((x - mean) / std) @ beta[1:], -3, 3)


def metrics(y: np.ndarray, pred: np.ndarray) -> dict:
    err = pred - y
    return {"n": int(len(y)), "mae": float(np.mean(np.abs(err))),
            "rmse": float(np.sqrt(np.mean(err**2))),
            "bias_prediction_minus_observed": float(np.mean(err)),
            "r2_vs_test_mean": float(1 - np.sum(err**2) / np.sum((y-y.mean())**2))}


def main() -> None:
    if RESULT.exists() or MODEL.exists():
        raise FileExistsError("Versioned external-survey outputs already exist")
    df, y, groups = prepare()
    train, test = grouped_split(groups)
    if set(groups[train]) & set(groups[test]):
        raise ValueError("Exact response vectors crossed train/test")
    # Fixed grouped folds within training only; one holdout used once.
    fold_groups = np.array_split(np.random.default_rng(1050).permutation(np.unique(groups[train])), 5)
    cv = []
    for name, columns in FEATURES.items():
        x = df[columns].to_numpy(dtype=float)
        for alpha in ALPHAS:
            errors = []
            for fold in fold_groups:
                valid_mask = np.isin(groups[train], fold)
                tr, va = train[~valid_mask], train[valid_mask]
                forecast = predict(x[va], fit_ridge(x[tr], y[tr], alpha))
                errors.extend(np.abs(forecast - y[va]).tolist())
            cv.append({"features": name, "alpha": alpha, "training_oof_mae": float(np.mean(errors))})
    selected = min(cv, key=lambda row: row["training_oof_mae"])
    holdout = {}
    predictions = {}
    for name, columns in FEATURES.items():
        x = df[columns].to_numpy(dtype=float)
        best_alpha = min((r for r in cv if r["features"] == name), key=lambda r: r["training_oof_mae"])["alpha"]
        forecast = predict(x[test], fit_ridge(x[train], y[train], best_alpha))
        predictions[name] = forecast
        holdout[name] = {"alpha_selected_on_training": best_alpha, **metrics(y[test], forecast)}
    baseline = np.repeat(y[train].mean(), len(test))
    picked = predictions[selected["features"]]
    rng = np.random.default_rng(1051)
    gains = []
    for _ in range(2000):
        idx = rng.integers(0, len(test), len(test))
        gains.append(float(np.mean(np.abs(y[test][idx]-baseline[idx]))
                           - np.mean(np.abs(y[test][idx]-picked[idx]))))
    segments = {}
    for name, mask in (("negative_lt_0", y[test] < 0), ("neutral_to_lt_1", (y[test] >= 0) & (y[test] < 1)),
                       ("positive_ge_1", y[test] >= 1)):
        segments[name] = {"n": int(mask.sum()), "mae": float(np.mean(np.abs(picked[mask]-y[test][mask]))) if mask.any() else None,
                          "bias": float(np.mean(picked[mask]-y[test][mask])) if mask.any() else None}
    current = df["Current users of ad blockers"].to_numpy(dtype=int)
    association = {str(value): {"n": int(np.sum(current == value)),
                                "intrusion_mean": float(np.mean(y[current == value]))}
                   for value in (0, 1)}
    output = {
        "version": "ad_blockers_intrusion_v1", "source": SOURCE_URL,
        "source_sha256": sha256(SOURCE), "license": "CC0 1.0 (publisher record)",
        "respondents": len(df), "target": "mean of ioa_1 through ioa_4, original -3 to +3 agreement scale",
        "target_mean": float(y.mean()), "target_sd": float(y.std()),
        "split": {"seed": SEED, "training": len(train), "test": len(test), "exact_answer_vector_grouped": True},
        "feature_sets": FEATURES, "training_only_grouped_5_fold_cv": cv, "selected_on_training_only": selected,
        "holdout_baseline": metrics(y[test], baseline), "holdout_feature_sets": holdout,
        "selected_model_segments": segments,
        "mae_gain_vs_training_mean_baseline_bootstrap_95pct": np.quantile(gains, [.025,.975]).tolist(),
        "clutter_intrusion_pearson": float(df.ad_clutter.corr(df.intrusion)),
        "current_ad_blocker_descriptive_association": association,
        "limitations": ["General website-ad interruption, not personalized-ad intrusiveness.",
                        "No ad stimuli, exposure treatments, per-person engagement, or level 0-4 definition.",
                        "All attitude predictors were measured in the same questionnaire; no causal inference.",
                        "No respondent ID; exact answer-vector grouping cannot detect repeated people with different responses."],
    }
    x = df[FEATURES[selected["features"]]].to_numpy(dtype=float)
    beta, mean, std = fit_ridge(x[train], y[train], selected["alpha"])
    MODEL.parent.mkdir(exist_ok=True)
    np.savez_compressed(MODEL, beta=beta, mean=mean, std=std,
                        features=np.array(FEATURES[selected["features"]]), alpha=selected["alpha"],
                        source_sha256=sha256(SOURCE), seed=SEED)
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"selected": selected, "holdout": holdout,
                      "baseline": output["holdout_baseline"], "segments": segments,
                      "gain_interval": output["mae_gain_vs_training_mean_baseline_bootstrap_95pct"]}, indent=2))


if __name__ == "__main__":
    main()
