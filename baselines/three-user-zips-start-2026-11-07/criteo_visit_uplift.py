"""Independent Criteo visit-uplift baseline for binary ad treatment.

This model is not connected to 49C users, privacy, creative text, or five
personalization levels. It uses treatment assignment and outcomes only during
training/evaluation; post-treatment exposure is excluded from predictors.
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "secondary_data/criteo-uplift/criteo_sample_200k.csv"
AUDIT = ROOT / "results/criteo_source_audit.json"
FEATURES = [f"f{i}" for i in range(12)]
SEED = 49
L2 = 0.001


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def fit_logistic(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, int]:
    """L2-regularized logistic regression with damped Newton steps."""
    design = np.column_stack((np.ones(len(x)), x))
    n = len(y)
    rate = float(y.mean())
    if not 0 < rate < 1:
        raise ValueError("Each treatment arm needs both visit outcomes")
    beta = np.zeros(design.shape[1])
    beta[0] = np.log(rate / (1 - rate))
    penalty = np.diag([0.0] + [L2] * x.shape[1])
    def objective(coefficients: np.ndarray) -> float:
        z = design @ coefficients
        return float(np.mean(np.logaddexp(0, z) - y * z)
                     + .5 * L2 * np.sum(coefficients[1:] ** 2))

    for step in range(50):
        pred = sigmoid(design @ beta)
        gradient = design.T @ (pred - y) / n + penalty @ beta
        weights = pred * (1 - pred)
        hessian = design.T @ (weights[:, None] * design) / n + penalty
        delta = np.linalg.solve(hessian, gradient)
        previous = objective(beta)
        scale = 1.0
        while scale > 1e-8 and objective(beta - scale * delta) > previous:
            scale *= .5
        if scale <= 1e-8:
            raise ArithmeticError("Newton line search did not improve the objective")
        beta -= scale * delta
        if np.max(np.abs(scale * delta)) < 1e-7:
            return beta, step + 1
    raise ArithmeticError("Logistic fit did not converge in 50 iterations")


def predict(x: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return sigmoid(beta[0] + x @ beta[1:])


def binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    p = np.clip(p, 1e-9, 1 - 1e-9)
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    ranks = pd.Series(p).rank(method="average").to_numpy()
    auc = (ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return {
        "n": len(y), "positives": n_pos, "rate": float(y.mean()),
        "roc_auc": float(auc), "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
    }


def arm_rate_difference(y: np.ndarray, treatment: np.ndarray) -> dict:
    treated = y[treatment == 1]
    control = y[treatment == 0]
    if not len(treated) or not len(control):
        raise ValueError("Both arms are required in every evaluation slice")
    p1, p0 = float(treated.mean()), float(control.mean())
    delta = p1 - p0
    se = np.sqrt(p1 * (1 - p1) / len(treated) + p0 * (1 - p0) / len(control))
    return {
        "treated_n": len(treated), "control_n": len(control),
        "treated_rate": p1, "control_rate": p0,
        "rate_difference": delta, "normal_95pct_interval": [delta - 1.96 * se, delta + 1.96 * se],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("random", "feature-group"), required=True)
    args = parser.parse_args()
    version = "v2" if args.split == "random" else "v3"
    result = ROOT / f"results/criteo_visit_uplift_{version}.json"
    model = ROOT / f"models/criteo_visit_uplift_{version}.npz"
    if model.exists() or result.exists():
        raise FileExistsError("Baseline artifact already exists; preserve it before another run")
    source_audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    df = pd.read_csv(SOURCE)
    if len(df) != source_audit["sample_size"]:
        raise ValueError("Sample size differs from the source audit")
    if df[FEATURES].isna().any().any() or not np.isfinite(df[FEATURES].to_numpy()).all():
        raise ValueError("Missing or non-finite feature values")
    if set(df["treatment"]) != {0, 1} or set(df["visit"]) != {0, 1}:
        raise ValueError("Unexpected treatment or visit codes")
    rng = np.random.default_rng(SEED)
    if args.split == "random":
        indices = rng.permutation(len(df))
        cut = round(.8 * len(indices))
        train_idx, test_idx = indices[:cut], indices[cut:]
        split_description = "seeded random row 80/20; no user ID is available for grouping"
    else:
        groups, unique_groups = pd.factorize(pd.MultiIndex.from_frame(df[FEATURES]))
        train_group_ids = rng.permutation(len(unique_groups))[:round(.8 * len(unique_groups))]
        is_train = np.isin(groups, train_group_ids)
        train_idx, test_idx = np.flatnonzero(is_train), np.flatnonzero(~is_train)
        split_description = "seeded 80/20 split by exact 12-feature vector; no user ID is available"
    raw = df[FEATURES].to_numpy(dtype=np.float64)
    mean = raw[train_idx].mean(axis=0)
    std = raw[train_idx].std(axis=0)
    std[std == 0] = 1
    x = np.clip((raw - mean) / std, -8, 8)
    treatment = df["treatment"].to_numpy(dtype=np.int8)
    visit = df["visit"].to_numpy(dtype=np.int8)
    conversion = df["conversion"].to_numpy(dtype=np.int8)
    betas = {}
    steps = {}
    arm_train_rates = {}
    for arm in (0, 1):
        arm_idx = train_idx[treatment[train_idx] == arm]
        betas[arm], steps[arm] = fit_logistic(x[arm_idx], visit[arm_idx])
        arm_train_rates[arm] = float(visit[arm_idx].mean())
    xt = x[test_idx]
    p0 = predict(xt, betas[0])
    p1 = predict(xt, betas[1])
    t_test = treatment[test_idx]
    y_test = visit[test_idx]
    outcome_metrics = {}
    for arm, forecast in ((0, p0), (1, p1)):
        mask = t_test == arm
        outcome_metrics[str(arm)] = {
            "constant": binary_metrics(y_test[mask], np.full(mask.sum(), arm_train_rates[arm])),
            "logistic": binary_metrics(y_test[mask], forecast[mask]),
        }
    uplift = p1 - p0
    order = np.argsort(-uplift)
    slices = []
    curve_x = [0.0]
    curve_y = [0.0]
    for fraction in np.arange(.1, 1.01, .1):
        k = round(len(test_idx) * fraction)
        chosen = order[:k]
        observed = arm_rate_difference(y_test[chosen], t_test[chosen])
        slices.append({"fraction_selected": round(float(fraction), 1), **observed})
        curve_x.append(float(fraction))
        curve_y.append(float(fraction) * observed["rate_difference"])
    all_visit = arm_rate_difference(y_test, t_test)
    all_conversion = arm_rate_difference(conversion[test_idx], t_test)
    auuc = float(np.trapezoid(curve_y, curve_x))
    random_auuc = .5 * all_visit["rate_difference"]
    output = {
        "source": source_audit["source"], "sample_seed": SEED,
        "split": split_description,
        "train_rows": len(train_idx), "test_rows": len(test_idx),
        "model": "two L2-logistic visit models, one per randomized treatment arm",
        "features": FEATURES, "excluded_predictors": ["treatment", "visit", "conversion", "exposure"],
        "regularization": L2, "newton_iterations_by_arm": {str(k): v for k, v in steps.items()},
        "visit_outcome_metrics_by_arm": outcome_metrics,
        "observed_test_visit_rate_difference": all_visit,
        "observed_test_conversion_rate_difference_descriptive": all_conversion,
        "visit_uplift_slices": slices,
        "auuc": auuc, "random_ranking_auuc": random_auuc,
        "auuc_gain_over_random": auuc - random_auuc,
        "limits": [
            "This is a binary ad-treatment uplift benchmark, not personalization-level optimization.",
            "No ad creative, privacy preferences, consent, or intrusiveness labels are present.",
            "Anonymized features cannot be mapped to 49C users or interpreted as business traits.",
            "Original trials were non-uniformly subsampled by the publisher; rates are benchmark-sample results, not original-population causal effects.",
            "No user ID is available for grouped validation; row split may be optimistic if latent users repeat.",
            "Individual treatment effects are unobserved; uplift ranking is evaluated through randomized-arm aggregates.",
        ],
    }
    model.parent.mkdir(exist_ok=True)
    np.savez_compressed(model, features=np.array(FEATURES), mean=mean, std=std,
                        beta_control=betas[0], beta_treated=betas[1], seed=SEED,
                        split=args.split)
    result.parent.mkdir(exist_ok=True)
    result.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"train": len(train_idx), "test": len(test_idx),
                      "visit_difference": all_visit, "auuc_gain_over_random": output["auuc_gain_over_random"],
                      "arm_metrics": outcome_metrics}, indent=2))


if __name__ == "__main__":
    main()
