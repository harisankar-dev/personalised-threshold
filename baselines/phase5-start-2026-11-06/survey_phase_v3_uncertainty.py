"""Phase 4 split-conformal audit; separate from the marketer app and V1/V2.

The Phase 3 candidate family is selected using only a model-fit partition.
A disjoint subset of V1's training partition calibrates uncertainty. The
previously examined V1 holdout is only a labelled reliability audit.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from survey_phase_v1 import ROOT, SAV, predict_ridge, regression_metrics, sha256
from survey_phase_v2 import CANDIDATES, grouped_cv, prepare, grouped_split


RESULT = ROOT / "results/survey_phase_v3_uncertainty.json"
MODEL = ROOT / "models/unsolicited_intrusiveness_respondent_v3_calibrated.npz"
V1_RESULT = ROOT / "results/survey_phase_v1.json"
V2_RESULT = ROOT / "results/survey_phase_v2.json"
SEED = 49
CALIBRATION_SEED = 4905
MIS_COVERAGE = 0.10


def finite_sample_quantile(residuals: np.ndarray, miscoverage: float = MIS_COVERAGE) -> float:
    """Conservative split-conformal order statistic, with finite-sample rank."""
    values = np.asarray(residuals, dtype=float)
    if values.ndim != 1 or len(values) < 1 or not np.isfinite(values).all():
        raise ValueError("Residuals must be a nonempty finite vector")
    if not 0 < miscoverage < 1:
        raise ValueError("Miscoverage must lie strictly between zero and one")
    rank = math.ceil((len(values) + 1) * (1 - miscoverage))
    if rank > len(values):
        raise ValueError("Calibration set too small for requested coverage")
    return float(np.sort(values)[rank - 1])


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> list[float]:
    if not 0 <= successes <= n or n < 1:
        raise ValueError("Invalid binomial count")
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [float(center - half), float(center + half)]


def main() -> None:
    if RESULT.exists() or MODEL.exists():
        raise FileExistsError("Phase 4 versioned artifacts already exist; preserve before deliberate rerun")
    v1 = json.loads(V1_RESULT.read_text(encoding="utf-8"))["respondent_survey"]
    v2 = json.loads(V2_RESULT.read_text(encoding="utf-8"))
    if sha256(SAV) != v2["source_sha256"] or sha256(SAV) != v1["sha256"]:
        raise ValueError("Survey source differs from V1/V2")
    df, y, groups = prepare()
    train, test = grouped_split(groups, SEED)
    if (len(train), len(test)) != (670, 167):
        raise ValueError("Original V1 holdout changed")
    fit_local, cal_local = grouped_split(groups[train], CALIBRATION_SEED)
    fit_idx, cal_idx = train[fit_local], train[cal_local]
    if set(groups[fit_idx]) & set(groups[cal_idx]) or set(groups[train]) & set(groups[test]):
        raise ValueError("Exact answer vectors crossed a partition")
    cv = grouped_cv(df, y, groups, fit_idx)
    selected = min(cv, key=lambda row: row["out_of_fold_mae"])
    columns = CANDIDATES[selected["candidate"]]
    x = df[columns].to_numpy(dtype=float)
    from survey_phase_v1 import fit_ridge
    fit = fit_ridge(x[fit_idx], y[fit_idx], alpha=selected["alpha"])
    cal_pred = predict_ridge(x[cal_idx], fit)
    test_pred = predict_ridge(x[test], fit)
    q_abs = finite_sample_quantile(np.abs(y[cal_idx] - cal_pred))
    q_upper = finite_sample_quantile(y[cal_idx] - cal_pred)
    lower = np.clip(test_pred - q_abs, 1, 7)
    upper = np.clip(test_pred + q_abs, 1, 7)
    one_sided_upper = np.clip(test_pred + q_upper, 1, 7)
    covered = (lower <= y[test]) & (y[test] <= upper)
    below_neutral = y[test] < 4
    near_neutral = (y[test] >= 4) & (y[test] < 5)
    high = y[test] >= 5
    segments = {}
    for name, mask in (("below_neutral_lt_4", below_neutral),
                       ("neutral_to_below_agreement_4_to_lt_5", near_neutral),
                       ("agreement_ge_5", high)):
        segments[name] = {"n": int(mask.sum()), "covered": int(covered[mask].sum()),
                          "empirical_coverage": float(covered[mask].mean()),
                          "mae": float(np.abs(test_pred[mask] - y[test][mask]).mean())}
    n_cover = int(covered.sum())
    output = {
        "version": "survey_phase_v3_uncertainty",
        "source_sha256": sha256(SAV),
        "recipe": {"origin": "five-fold grouped CV inside model-fit partition only", "candidate": selected["candidate"],
                   "alpha": selected["alpha"], "features": columns},
        "model_fit_cross_validation": cv,
        "split": {"original_training": len(train), "model_fit": len(fit_idx),
                  "calibration": len(cal_idx), "previously_examined_holdout": len(test),
                  "outer_seed": SEED, "calibration_seed": CALIBRATION_SEED,
                  "exact_answer_vector_grouped": True},
        "nominal_marginal_coverage": 1 - MIS_COVERAGE,
        "absolute_calibration_quantile": q_abs,
        "one_sided_upper_calibration_quantile": q_upper,
        "point_metrics_on_reused_holdout": regression_metrics(y[test], test_pred),
        "two_sided_interval": {"covered": n_cover,
                               "empirical_coverage": n_cover / len(test),
                               "wilson_95pct_interval_for_observed_coverage": wilson_interval(n_cover, len(test)),
                               "median_width": float(np.median(upper - lower)),
                               "mean_width": float(np.mean(upper - lower)),
                               "segments": segments},
        "one_sided_upper_audit": {
            "upper_below_agreement_5": int((one_sided_upper < 5).sum()),
            "observed_high_ge_5_with_upper_below_5": int(np.sum(high & (one_sided_upper < 5))),
            "observed_high_ge_5_n": int(high.sum()),
            "upper_covers_observed": int(np.sum(y[test] <= one_sided_upper)),
            "empirical_upper_coverage": float(np.mean(y[test] <= one_sided_upper)),
        },
        "limitations": [
            "The outer holdout was examined in V1/V2, so this is not fresh validation.",
            "Split-conformal guarantees require exchangeability; this convenience survey cannot establish it for future people or ads.",
            "Marginal interval coverage does not imply coverage for high- or low-intrusion subgroups.",
            "Predictors are contemporaneous questionnaire answers and cannot be extracted from uploaded ad creatives.",
            "No personalization treatments, consent contexts, or engagement outcomes are linked to these respondents.",
        ],
    }
    MODEL.parent.mkdir(exist_ok=True)
    beta, mean, std = fit
    np.savez_compressed(MODEL, beta=beta, mean=mean, std=std, features=np.array(columns),
                        alpha=selected["alpha"], calibration_absolute_quantile=q_abs,
                        calibration_upper_quantile=q_upper, source_sha256=sha256(SAV))
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
