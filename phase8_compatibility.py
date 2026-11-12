"""Evidence-labelled, non-predictive consumer–ad compatibility review.

The current datasets do not link an uploaded creative to a measured response
from this campaign's audience. This module therefore never emits a fit score,
segment assignment, conversion probability, or personalization threshold.
"""
from __future__ import annotations


CATEGORIES = {"unknown", "retail", "food", "technology", "travel", "education", "finance", "health", "other"}
CHANNELS = {"unknown", "social", "search", "display", "email", "other"}
DATA_SOURCES = {"unknown", "none", "page_context", "broad_demographic", "first_party_behavior",
                "first_party_purchase", "third_party", "combined", "other"}
PERSONAL_SOURCES = {"broad_demographic", "first_party_behavior", "first_party_purchase", "third_party", "combined"}
METHOD_FOR_SOURCE = {
    "none": {"generic"},
    "page_context": {"contextual"},
    "broad_demographic": {"demographic", "combined"},
    "first_party_behavior": {"behavioral", "combined"},
    "first_party_purchase": {"historical", "combined"},
    "combined": {"combined"},
}
SURVEILLANCE_CUES = {"private_activity_claim", "direct_identifier", "observed_behavior", "sensitive_personal_fact",
                     "precise_location", "purchase_history", "browsing_history", "explicit_surveillance",
                     "combined_signals", "specific_activity_detail", "no_consent", "sensitive_targeting",
                     "behavioral_targeting", "precise_location_targeting"}
PRESSURE_CUES = {"countdown_pressure", "scarcity_claim", "extreme_discount", "urgent_call_to_action",
                 "alarmist_claim", "excessive_exclamation"}


def _choice(campaign: dict, field: str, choices: set[str]) -> str:
    value = campaign.get(field, "unknown")
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"Choose a valid {field.replace('_', ' ')}.")
    return value


def assess(campaign: dict, creative: dict, strategy: dict) -> dict:
    """Return only observed/declared signals and explicit evidence gaps."""
    if not isinstance(campaign, dict) or not isinstance(creative, dict) or not isinstance(strategy, dict):
        raise ValueError("Campaign, creative and strategy must be objects.")
    category = _choice(campaign, "product_category", CATEGORIES)
    channel = _choice(campaign, "channel", CHANNELS)
    source = _choice(campaign, "data_source", DATA_SOURCES)
    method = strategy["targeting_method"]
    consent = strategy["consent_status"]
    eligibility = strategy["audience_eligibility"]
    cues = sorted({item.get("cue") for item in creative.get("evidence", [])
                   if isinstance(item, dict) and isinstance(item.get("cue"), str)})
    source_mismatch = source in METHOD_FOR_SOURCE and method not in METHOD_FOR_SOURCE[source]
    source_permission_missing = source in PERSONAL_SOURCES and (consent != "yes" or eligibility != "yes")
    source_unspecified_for_personal_method = (method in {"demographic", "behavioral", "historical", "combined"}
                                              and source in {"unknown", "other"})
    source_review = (source in {"third_party", "other"} or source_mismatch or source_permission_missing
                     or source_unspecified_for_personal_method)
    signals = []
    if cues:
        if any(cue in SURVEILLANCE_CUES for cue in cues):
            signals.append("Visible personal-data or tracking references require review against actual data use.")
        if any(cue in PRESSURE_CUES for cue in cues):
            signals.append("Pressure wording is present; compare one calmer version before launch.")
    if not signals:
        signals.append("No mapped privacy or pressure wording was found; visual and consumer responses remain unmeasured.")
    checks = []
    if source == "unknown":
        checks.append("Declare the data source before assessing how the targeting method operates.")
    if source_mismatch:
        checks.append("Declared data source and targeting method do not match; verify the actual campaign configuration.")
    if source_permission_missing:
        checks.append("This personal-data source needs verified permission and audience eligibility before use.")
    if source == "third_party":
        checks.append("Third-party data rights and permitted purpose require separate review; the app cannot verify them.")
    if source == "other" or source_unspecified_for_personal_method:
        checks.append("The data source is unresolved for this targeting method; review it before launch.")
    if category == "unknown":
        checks.append("Specify a product category so the test plan can use the actual offer context.")
    if channel == "unknown":
        checks.append("Specify the advertising channel; placement and format may change the consumer response.")
    if creative.get("tier") == "needs_review":
        checks.append("The creative is not assessable from the available text; inspect its visual content before launch.")
    checks.append("For a genuine compatibility estimate, measure relevance and direct intrusiveness for this creative and eligible audience in a controlled comparison.")
    return {
        "status": "research_informed_review_only",
        "mode": "A",
        "product_category_declared": category,
        "channel_declared": channel,
        "data_source_declared": source,
        "targeting_method_declared": method,
        "data_source_review_required": source_review,
        "creative_signals": signals,
        "prelaunch_checks": checks,
        "evidence": {
            "creative_cues": "heuristic_screen_of_observable_text",
            "campaign_context": "marketer_declared_unverified",
            "survey_profiles": "separate_aggregate_descriptions",
            "ad_consumer_response": "unavailable_for_this_creative_and_audience",
            "financial_scenarios": "user_defined_hypotheses",
        },
        "consumer_relevance_prediction": None,
        "consumer_intrusiveness_prediction": None,
        "consumer_segment_assignment": None,
        "expected_incremental_conversions": None,
        "compatibility_score": None,
        "five_level_threshold_status": "insufficient_evidence",
        "next_test": "Within one eligible campaign, compare the current creative with one revision; record exposure, direct relevance and intrusiveness ratings, and engagement on the same exposure. Keep respondent and ad groups separate during validation.",
    }
