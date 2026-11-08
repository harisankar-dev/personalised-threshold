"""Curated, aggregate-only research view from saved 49-C experiment results.

The dashboard never runs a research model on a marketer's uploaded creative.
Each metric retains its source, target and validation scope.
"""
from __future__ import annotations

import json
from pathlib import Path

from threshold_engine import LEVELS, REQUIRED_EVIDENCE, current_dataset_status


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def result(name: str) -> dict:
    path = RESULTS / name
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Research result is malformed: {name}")
    return data


def dashboard_data() -> dict:
    event = result("baseline.json")
    criteo = result("criteo_visit_uplift_v3.json")
    uplift = result("criteo_uplift_validation_v3.json")
    v1 = result("survey_phase_v1.json")
    v2 = result("survey_phase_v2.json")
    v3 = result("survey_phase_v3_uncertainty.json")
    independent = result("ad_blockers_intrusion_v1.json")
    vietnam = result("vietnam_privacy_trust_v1.json")
    status = current_dataset_status()
    return {
        "scope": "Saved aggregate research results only; none of these models scores an uploaded ad.",
        "engagement": {
            "upad": {
                "source": "results/baseline.json", "target": event["label"],
                "holdout_n": event["test_rows"],
                "constant_auc": event["constant_baseline"]["roc_auc"],
                "logistic_auc": event["regularized_logistic"]["roc_auc"],
                "constant_brier": event["constant_baseline"]["brier"],
                "logistic_brier": event["regularized_logistic"]["brier"],
            },
            "criteo": {
                "source": "results/criteo_visit_uplift_v3.json; results/criteo_uplift_validation_v3.json",
                "target": "Visit after binary ad treatment/control; no intrusiveness target",
                "train_n": criteo["train_rows"], "holdout_n": criteo["test_rows"],
                "control": criteo["visit_outcome_metrics_by_arm"]["0"],
                "treatment": criteo["visit_outcome_metrics_by_arm"]["1"],
                "auuc_gain": uplift["observed_auuc_gain_over_random"],
                "auuc_gain_interval": uplift["row_bootstrap_95pct_interval_auuc_gain"],
            },
        },
        "intrusiveness": {
            "romano_han": {
                "source": "results/survey_phase_v1.json; results/survey_phase_v2.json; results/survey_phase_v3_uncertainty.json",
                "target": "Mean of six direct general unsolicited-ad intrusion items, 1–7",
                "respondents": v1["respondent_survey"]["respondents"],
                "holdout_n": v2["holdout_metrics"]["v1_saved_model"]["n"],
                "baseline_mae": v2["holdout_metrics"]["training_mean_baseline"]["mae"],
                "v1_mae": v2["holdout_metrics"]["v1_saved_model"]["mae"],
                "v2_mae": v2["holdout_metrics"]["v2_cv_selected"]["mae"],
                "v2_gain_interval": v2["mae_gain_v2_over_v1_95pct_interval"],
                "privacy_intrusion_pearson": v2["construct_overlap"]["pearson_composite_privacy_intrusion"],
                "high_n": v2["false_reassurance"]["v2"]["high_n"],
                "high_below_5_v1": v2["false_reassurance"]["v1"]["high_predicted_below_agreement_5"],
                "high_below_5_v2": v2["false_reassurance"]["v2"]["high_predicted_below_agreement_5"],
                "low_n": v3["two_sided_interval"]["segments"]["below_neutral_lt_4"]["n"],
                "low_interval_covered": v3["two_sided_interval"]["segments"]["below_neutral_lt_4"]["covered"],
                "overall_interval_covered": v3["two_sided_interval"]["covered"],
                "overall_interval_n": v3["split"]["previously_examined_holdout"],
                "high_upper_below_5": v3["one_sided_upper_audit"]["observed_high_ge_5_with_upper_below_5"],
            },
            "independent_web_ads": {
                "source": "results/ad_blockers_intrusion_v1.json",
                "target": "General web-ad intrusion, −3 to +3; different scale and predictors",
                "respondents": independent["respondents"],
                "holdout_n": independent["holdout_baseline"]["n"],
                "baseline_mae": independent["holdout_baseline"]["mae"],
                "model_mae": independent["holdout_feature_sets"]["C_plus_clutter"]["mae"],
                "negative_n": independent["selected_model_segments"]["negative_lt_0"]["n"],
                "negative_mae": independent["selected_model_segments"]["negative_lt_0"]["mae"],
            },
        },
        "privacy_trust": {
            "vietnam": {
                "source": "results/vietnam_privacy_trust_v1.json",
                "respondents": vietnam["respondents"],
                "trust_purchase_rho": vietnam["predeclared_descriptive_associations"]["online_trust_vs_purchase_intention"]["spearman_rho"],
                "trust_purchase_interval": vietnam["predeclared_descriptive_associations"]["online_trust_vs_purchase_intention"]["row_bootstrap_95pct_interval"],
                "target": "Online-store trust and stated purchase intention; no ad or intrusion label",
            },
            "genz": {
                "source": "results/survey_phase_v1.json",
                "respondents": v1["genz_survey"]["respondents"],
                "personalization_privacy_rho": v1["genz_survey"]["spearman_correlations"]["perceived_personalization"]["privacy_concern"],
                "personalization_purchase_rho": v1["genz_survey"]["spearman_correlations"]["perceived_personalization"]["purchase_reaction"],
                "target": "Self-reported perceived personalization, privacy concern and purchase reaction; no direct intrusion or assigned treatment",
            },
        },
        "threshold": {
            "status": status["status"], "reason": status["reason"],
            "required_evidence": list(REQUIRED_EVIDENCE),
            "missing": status["missing"],
            "levels": [{"level": level, "name": name} for level, name in LEVELS.items()],
            "recommended_level": status["recommended_level"],
        },
    }
