"""Research-only evaluation of OSF location-targeting experimental conditions.

Reads only six non-identifying columns from the user's local workbooks. Writes
aggregate results, never respondent records or a deployable individual model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split


FILES = {
    "study_1": ("study_1/01_data/study1_data.xlsx", "a614b914d193bdba9436d6c9d896f70b3a16c7a474bfb3205ac7c7ae45ce0276"),
    "study_2": ("study_2/01_data/study2_data.xlsx", "3080faaf4dfde1e5cb8a220c95c71fdd191d6f75361f7433572e5d47c24973ef"),
}
COLUMNS = ("Targ", "Trans", "PPI", "PPR", "PP", "ITC")


def load_study(path: Path, expected_hash: str) -> pd.DataFrame:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f"Source hash changed: {path.name}")
    frame = pd.read_excel(path, usecols=lambda column: column in COLUMNS)
    if set(frame.columns) != set(COLUMNS):
        raise ValueError(f"Required columns missing: {path.name}")
    if frame[list(COLUMNS)].isna().any().any():
        raise ValueError(f"Missing experimental or outcome values: {path.name}")
    for column in ("Targ", "Trans"):
        if not frame[column].isin((0, 1)).all():
            raise ValueError(f"Unexpected {column} code: {path.name}")
    for column in ("PPI", "PPR", "PP", "ITC"):
        if not pd.api.types.is_numeric_dtype(frame[column]) or not frame[column].between(1, 7).all():
            raise ValueError(f"Unexpected {column} scale: {path.name}")
    return frame.loc[:, COLUMNS].copy()


def cells(frame: pd.DataFrame) -> np.ndarray:
    return (frame["Targ"].to_numpy(dtype=int) * 2 + frame["Trans"].to_numpy(dtype=int))


def predict_cell_mean(train: pd.DataFrame, target: pd.DataFrame) -> np.ndarray:
    means = train.groupby(["Targ", "Trans"])["PPI"].mean()
    return np.array([means.loc[(targ, trans)] for targ, trans in zip(target.Targ, target.Trans)], dtype=float)


def error_summary(observed: np.ndarray, predicted: np.ndarray) -> dict:
    high = observed >= 5
    return {
        "mae": float(np.mean(np.abs(observed - predicted))),
        "rmse": float(np.sqrt(np.mean((observed - predicted) ** 2))),
        "high_observed_count": int(high.sum()),
        "high_predicted_below_5": int(np.sum(high & (predicted < 5))),
        "high_predicted_below_4": int(np.sum(high & (predicted < 4))),
        "mean_error_high": float(np.mean(predicted[high] - observed[high])) if high.any() else None,
    }


def interval(values: np.ndarray, *, seed: int, resamples: int = 2000) -> list[float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(resamples, len(values)))
    return [float(x) for x in np.quantile(values[indices].mean(axis=1), [0.025, 0.975])]


def evaluate(frame: pd.DataFrame, *, seed: int) -> dict:
    labels = cells(frame)
    train_index, test_index = train_test_split(
        np.arange(len(frame)), test_size=0.25, random_state=seed, stratify=labels
    )
    train, test = frame.iloc[train_index], frame.iloc[test_index]
    observed = test.PPI.to_numpy(dtype=float)
    baseline = np.full(len(test), train.PPI.mean(), dtype=float)
    candidate = predict_cell_mean(train, test)
    improvement = np.abs(observed - baseline) - np.abs(observed - candidate)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    cv = []
    for fit_idx, validation_idx in folds.split(train, cells(train)):
        fit, validation = train.iloc[fit_idx], train.iloc[validation_idx]
        y = validation.PPI.to_numpy(dtype=float)
        cv.append({
            "global_mean_mae": float(np.mean(np.abs(y - fit.PPI.mean()))),
            "condition_mean_mae": float(np.mean(np.abs(y - predict_cell_mean(fit, validation)))),
        })
    groups = []
    for (targ, trans), group in frame.groupby(["Targ", "Trans"], sort=True):
        entry = {"targeting_code": int(targ), "disclosure_code": int(trans), "n": int(len(group))}
        for column in ("PPI", "PPR", "ITC"):
            values = group[column].to_numpy(dtype=float)
            entry[column] = {"mean": float(values.mean()), "mean_95pct_bootstrap_ci": interval(values, seed=seed + int(targ) * 10 + int(trans) + len(column))}
        groups.append(entry)
    return {
        "n": len(frame), "train_n": len(train), "test_n": len(test),
        "outcome_scale": "PPI 1-7, higher is more privacy intrusive",
        "baseline_global_training_mean": error_summary(observed, baseline),
        "candidate_training_condition_mean": error_summary(observed, candidate),
        "candidate_mae_gain_over_global_mean": float(improvement.mean()),
        "candidate_mae_gain_95pct_test_bootstrap_ci": interval(improvement, seed=seed + 99),
        "train_only_5fold_cv_mean_mae": {
            key: float(np.mean([fold[key] for fold in cv])) for key in cv[0]
        },
        "observed_condition_groups": groups,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="Local replication folder; no download")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; use a new versioned path")
    result = {"status": "research_only", "source": "Verenkotte-Spann OSF location-targeting replication",
              "rights_note": "User supplied local files and asserted research/model-training use; no source-specific dataset license verified",
              "individual_model": "unsupported: only assigned condition inputs are available before exposure",
              "five_level_threshold": "insufficient_evidence", "studies": {}}
    for i, (study, (relative, expected_hash)) in enumerate(FILES.items()):
        frame = load_study(args.root / relative, expected_hash)
        result["studies"][study] = {"source_sha256": expected_hash, **evaluate(frame, seed=4900 + i)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote aggregate results: {args.output}")


if __name__ == "__main__":
    main()
