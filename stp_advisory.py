"""Conservative, budget-aware Phase 7 STP advisory and scenario arithmetic.

This component has no fitted customer-response model. It never estimates
uplift, audience membership, or a five-level personalization threshold.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
from pathlib import Path
import re


MONEY_LIMIT = Decimal("1000000000000")
OBJECTIVES = {"unknown", "awareness", "traffic", "conversions"}
METHODS = {"unknown", "generic", "contextual", "demographic", "behavioral", "historical", "combined", "sensitive"}
CHECKS = {"unknown", "yes", "no"}
SCENARIO_OPTIONS = {"revise_one_creative", "adjust_targeting", "one_variant", "multiple_variants"}
DATA_SOURCES = {"unknown", "none", "page_context", "broad_demographic", "first_party_behavior",
                "first_party_purchase", "third_party", "combined", "other"}
SOURCE_METHODS = {"none": {"generic"}, "page_context": {"contextual"},
                  "broad_demographic": {"demographic", "combined"},
                  "first_party_behavior": {"behavioral", "combined"},
                  "first_party_purchase": {"historical", "combined"}, "combined": {"combined"}}
PERSONAL_SOURCES = {"broad_demographic", "first_party_behavior", "first_party_purchase", "third_party", "combined"}
OPTION_ORDER = ("keep_current_campaign", "revise_one_creative", "adjust_targeting", "one_variant", "multiple_variants")
OPTION_NAMES = {
    "keep_current_campaign": "Keep current campaign",
    "revise_one_creative": "Revise one creative",
    "adjust_targeting": "Adjust targeting in the same campaign",
    "one_variant": "Test one additional variant",
    "multiple_variants": "Consider multiple segment-specific variants",
}
COST_INPUTS = ("revision_cost", "targeting_cost", "variant_cost", "segmentation_cost", "management_cost")
BASELINE_INPUTS = ("cpc", "cpm", "conversion_rate_pct", "contribution_margin", "audience_reach")
SCENARIO_INPUTS = ("worst_incremental_conversions", "central_incremental_conversions", "best_incremental_conversions")
PERSONA_SOURCE = Path(__file__).resolve().parent / "results" / "phase7_segmentation_v1.json"


def _number(data: dict, name: str, *, integer: bool = False, ceiling: Decimal = MONEY_LIMIT) -> Decimal | None:
    value = data.get(name)
    if value is None or value == "":
        return None
    if isinstance(value, bool) or isinstance(value, (dict, list)):
        raise ValueError(f"{name.replace('_', ' ').capitalize()} must be a non-negative number.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name.replace('_', ' ').capitalize()} must be a non-negative number.") from exc
    if not number.is_finite() or number < 0 or number > ceiling or (integer and number != number.to_integral_value()):
        raise ValueError(f"{name.replace('_', ' ').capitalize()} is outside the allowed range.")
    return number


def _choice(data: dict, name: str, choices: set[str], default: str) -> str:
    value = data.get(name, default)
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"Choose a valid {name.replace('_', ' ')}.")
    return value


def _money(value: Decimal | None) -> str | None:
    return format(value.quantize(Decimal("0.01")), ".2f") if value is not None else None


def _sum_if_known(*parts: Decimal | None) -> Decimal | None:
    return sum(parts, Decimal(0)) if all(part is not None for part in parts) else None


def survey_personas() -> dict:
    """Return source-separated aggregate survey profiles; never individual rows."""
    if not PERSONA_SOURCE.is_file():
        return {"status": "unavailable", "reason": "The separate survey profile audit is unavailable."}
    saved = json.loads(PERSONA_SOURCE.read_text(encoding="utf-8"))
    return {
        "status": "descriptive_only",
        "message": "These are survey response patterns, not members of this campaign audience or predicted ad outcomes.",
        "sources": {
            name: {"respondents": saved[name]["respondents"],
                   "construct": saved[name]["construct"],
                   "counts": saved[name]["counts"],
                   "shares": saved[name]["shares"]}
            for name in ("genz", "romano_han")
        },
    }


def evaluate(campaign: dict, creative: dict) -> dict:
    """Compare minimum-change options without making an unsupported uplift claim.

    `total_budget` includes existing committed media/operations and any new
    production/management/segmentation cost. No media reallocation is assumed.
    """
    if not isinstance(campaign, dict):
        raise ValueError("Campaign details must be a JSON object.")
    currency = campaign.get("currency", "INR")
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("Currency must be a three-letter uppercase code.")
    objective = _choice(campaign, "objective", OBJECTIVES, "unknown")
    method = _choice(campaign, "targeting_method", METHODS, "unknown")
    data_source = _choice(campaign, "data_source", DATA_SOURCES, "unknown")
    consent = _choice(campaign, "consent_status", CHECKS, "unknown")
    eligibility = _choice(campaign, "audience_eligibility", CHECKS, "unknown")
    total_budget = _number(campaign, "total_budget")
    committed = _number(campaign, "committed_spend")
    if total_budget is not None and committed is not None and committed > total_budget:
        raise ValueError("Committed spend cannot exceed the total campaign budget.")
    costs = {name: _number(campaign, name) for name in COST_INPUTS}
    baseline = {name: _number(campaign, name, integer=(name == "audience_reach"),
                              ceiling=Decimal(100) if name == "conversion_rate_pct" else MONEY_LIMIT)
                for name in BASELINE_INPUTS}
    scenario_option = _choice(campaign, "scenario_option", SCENARIO_OPTIONS, "one_variant")
    scenarios = {name: _number(campaign, name, integer=True, ceiling=Decimal("1000000000"))
                 for name in SCENARIO_INPUTS}
    for earlier, later in ((SCENARIO_INPUTS[0], SCENARIO_INPUTS[1]),
                           (SCENARIO_INPUTS[1], SCENARIO_INPUTS[2]),
                           (SCENARIO_INPUTS[0], SCENARIO_INPUTS[2])):
        if scenarios[earlier] is not None and scenarios[later] is not None and scenarios[earlier] > scenarios[later]:
            raise ValueError("Scenario conversions must increase from worst to central to best.")
    variant_count = _number(campaign, "variant_count", integer=True, ceiling=Decimal(20))
    if variant_count is not None and variant_count < 2:
        raise ValueError("Multiple variants requires at least two additional variants.")
    margin = baseline["contribution_margin"]
    remaining = total_budget - committed if total_budget is not None and committed is not None else None

    option_costs = {
        "keep_current_campaign": Decimal(0),
        "revise_one_creative": costs["revision_cost"],
        "adjust_targeting": _sum_if_known(costs["targeting_cost"], costs["management_cost"]),
        "one_variant": _sum_if_known(costs["variant_cost"], costs["management_cost"], costs["segmentation_cost"]),
        "multiple_variants": _sum_if_known(
            costs["variant_cost"] * variant_count if costs["variant_cost"] is not None and variant_count is not None else None,
            costs["management_cost"], costs["segmentation_cost"]),
    }
    cues = {item.get("cue") for item in creative.get("evidence", []) if isinstance(item, dict)}
    tier = creative.get("tier")
    source_mismatch = data_source in SOURCE_METHODS and method not in SOURCE_METHODS[data_source]
    source_unverified = data_source in PERSONAL_SOURCES and (consent != "yes" or eligibility != "yes")
    source_unspecified_for_personal_method = (method in {"demographic", "behavioral", "historical", "combined"}
                                              and data_source in {"unknown", "other"})
    privacy_blocker = (source_mismatch or source_unverified or source_unspecified_for_personal_method or
                       data_source in {"third_party", "other"} or
                       method == "sensitive" or eligibility == "no" or "no_consent" in cues or
                       (method in {"demographic", "behavioral", "historical", "combined"} and
                        (consent != "yes" or eligibility != "yes")))
    privacy_status = ("Hold for review" if privacy_blocker else
                      "Unverified" if method == "unknown" or eligibility == "unknown" else "Declared eligible")
    options = []
    for key in OPTION_ORDER:
        cost = option_costs[key]
        affordable = None if cost is None or remaining is None else cost <= remaining
        break_even = None
        if cost is not None and margin is not None and margin > 0:
            break_even = int((cost / margin).to_integral_value(rounding=ROUND_CEILING))
        options.append({
            "key": key,
            "name": OPTION_NAMES[key],
            "incremental_implementation_cost": _money(cost),
            "budget_feasible": affordable,
            "permission_status": privacy_status,
            "remaining_budget_after_option": _money(remaining - cost) if affordable is True else None,
            "break_even_incremental_conversions": break_even,
            "evidence_status": "existing_campaign_comparator" if key == "keep_current_campaign" else
                               "editorial_hypothesis" if key == "revise_one_creative" else
                               "no_validated_segment_level_lift",
        })

    scenario_cost = option_costs[scenario_option]
    scenario_results = {}
    for key in SCENARIO_INPUTS:
        estimate = scenarios[key]
        scenario_results[key.removesuffix("_incremental_conversions")] = {
            "user_entered_incremental_conversions": int(estimate) if estimate is not None else None,
            "net_incremental_value": _money(estimate * margin - scenario_cost)
            if estimate is not None and margin is not None and scenario_cost is not None else None,
        }

    if privacy_blocker:
        action = "hold_for_review"
        reason = "Targeting method, data source, permission or audience eligibility needs review; do not launch this targeting configuration."
    elif tier == "needs_review" or tier is None:
        action = "hold_for_review"
        reason = "The creative lacks enough assessable text; review it before a launch decision."
    elif tier in {"moderate_intrusive", "high_intrusive"}:
        if remaining is not None and costs["revision_cost"] is not None and costs["revision_cost"] > remaining:
            action = "hold_for_review"
            reason = "The creative has review cues and the entered revision cost exceeds available budget headroom."
        else:
            action = "revise_one_creative"
            reason = "Review the matched wording and test one revised creative within the existing campaign; its performance benefit is unverified."
    else:
        action = "keep_current_campaign"
        reason = "Keep the current campaign. Available evidence does not justify additional segmentation costs."

    missing = [name for name in ("total_budget", "committed_spend", *COST_INPUTS, *BASELINE_INPUTS,
                                "variant_count", *SCENARIO_INPUTS) if
               (campaign.get(name) is None or campaign.get(name) == "")]
    warnings = ["Survey personas are exploratory and cannot identify members of this campaign audience.",
                "No validated incremental response or consumer-specific intrusion estimate exists for these options."]
    if objective == "unknown":
        warnings.append("Campaign objective was not specified; objective fit cannot be assessed.")
    elif objective in {"awareness", "traffic"} and margin is not None:
        warnings.append("Conversion break-even is a financial check, not a validated success measure for this campaign objective.")
    if method == "unknown":
        warnings.append("Targeting method was not declared; privacy/eligibility screening is incomplete.")
    if data_source == "unknown":
        warnings.append("The actual targeting data source was not declared; method assessment is incomplete.")
    if source_mismatch:
        warnings.append("The declared targeting method and data source conflict; verify campaign configuration before launch.")
    if data_source == "third_party":
        warnings.append("Third-party data rights and permitted purpose need separate verification before this targeting can launch.")
    if data_source == "other" or source_unspecified_for_personal_method:
        warnings.append("The targeting data source is unresolved for this method; review it before launch.")
    if consent == "unknown" or eligibility == "unknown":
        warnings.append("Consent or audience eligibility is unverified; no new personalized targeting is recommended.")
    if remaining is None:
        warnings.append("Budget headroom is unknown; option affordability cannot be established.")
    if baseline["audience_reach"] is None:
        warnings.append("Audience reach is unknown; fragmentation risk cannot be quantified.")
    else:
        warnings.append("Reach alone does not establish enough responses per variant; no multi-variant recommendation is made.")
    return {
        "status": "exploratory_advisory",
        "action": action,
        "reason": reason,
        "basis": "creative cue rubric, declared targeting checks, and user-entered costs only",
        "validated_incremental_performance": False,
        "validated_audience_segment": False,
        "five_level_threshold_status": "insufficient_evidence",
        "currency": currency,
        "objective": objective,
        "targeting_method": method,
        "data_source": data_source,
        "consent_status": consent,
        "audience_eligibility": eligibility,
        "budget_scope": "Total budget includes existing committed campaign spend and all additional production, management and segmentation costs; no media reallocation or extra media spend is assumed.",
        "total_budget": _money(total_budget),
        "committed_spend": _money(committed),
        "available_budget_headroom": _money(remaining),
        "baseline_metrics_user_entered": {key: _money(value) if key != "audience_reach" else
                                          int(value) if value is not None else None
                                          for key, value in baseline.items()},
        "missing_inputs": missing,
        "options": options,
        "scenario": {
            "label": "User-defined hypothetical sensitivity check; not predicted uplift or company performance.",
            "option": scenario_option,
            "results": scenario_results,
            "calculation": "Net incremental value = user-entered incremental conversions × user-entered contribution margin − additional implementation cost. Baseline media spend is held fixed.",
        },
        "warnings": warnings,
    }
