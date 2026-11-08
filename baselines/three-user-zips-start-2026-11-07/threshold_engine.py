"""Consent-constrained personalization decision logic.

No current 49C data satisfy the evidence gate. This module is an executable
decision contract for future *measured* per-level predictions, not a fitted
personalization model.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


LEVELS = {
    0: "Generic",
    1: "Contextual or demographic",
    2: "Behavioural",
    3: "Historical",
    4: "Combined hyper-personalized",
}
REQUIRED_EVIDENCE = (
    "valid_engagement_outcome",
    "direct_intrusiveness_labels",
    "per_level_exposure_variation",
    "held_out_validation",
)


@dataclass(frozen=True)
class LevelEstimate:
    level: int
    engagement: float
    engagement_lower: float
    engagement_upper: float
    intrusion: float
    intrusion_lower: float
    intrusion_upper: float

    def validate(self) -> None:
        if self.level not in LEVELS:
            raise ValueError("Personalization level must be 0 through 4")
        if not 0 <= self.engagement_lower <= self.engagement <= self.engagement_upper <= 1:
            raise ValueError("Engagement estimate and bounds must be ordered within 0–1")
        if not 0 <= self.intrusion_lower <= self.intrusion <= self.intrusion_upper <= 1:
            raise ValueError("Intrusion estimate and bounds must be ordered within 0–1")


def recommend(
    estimates: list[LevelEstimate],
    *,
    eligible_levels: set[int],
    consent_verified: bool = False,
    max_intrusion_risk: float,
    evidence: dict[str, bool],
) -> dict:
    """Recommend only with measured evidence, explicit eligibility, and risk bounds.

    Uses the lower engagement bound among eligible levels whose upper intrusion
    bound is within the ceiling. Ties select the less personalized level.
    """
    if not 0 <= max_intrusion_risk <= 1:
        raise ValueError("Risk ceiling must be within 0–1")
    if any(level not in LEVELS for level in eligible_levels):
        raise ValueError("Eligible levels must be 0 through 4")
    if 0 not in eligible_levels:
        raise ValueError("Generic level 0 must be included as a fallback")
    allowed_levels = eligible_levels if consent_verified else {0}
    missing = [name for name in REQUIRED_EVIDENCE if evidence.get(name) is not True]
    if missing:
        return {
            "status": "insufficient_evidence", "recommended_level": None,
            "missing": missing, "eligible_levels": sorted(allowed_levels),
            "consent_verified": consent_verified,
            "reason": "The current evidence cannot support a consumer-level personalization threshold.",
        }
    if not estimates:
        return {"status": "insufficient_evidence", "recommended_level": None,
                "missing": ["per_level_estimates"], "eligible_levels": sorted(allowed_levels),
                "consent_verified": consent_verified,
                "reason": "No valid per-level estimates were supplied."}
    for item in estimates:
        item.validate()
    by_level = {item.level: item for item in estimates}
    if len(by_level) != len(estimates):
        raise ValueError("Each level can have only one estimate")
    unestimated = allowed_levels - set(by_level)
    if unestimated:
        return {"status": "insufficient_evidence", "recommended_level": None,
                "missing": [f"estimates_for_levels_{sorted(unestimated)}"],
                "eligible_levels": sorted(allowed_levels),
                "consent_verified": consent_verified,
                "reason": "At least one eligible level has no estimate."}
    feasible = [by_level[level] for level in allowed_levels
                if by_level[level].intrusion_upper <= max_intrusion_risk]
    if not feasible:
        return {"status": "risk_ceiling_exceeded", "recommended_level": None,
                "eligible_levels": sorted(allowed_levels),
                "consent_verified": consent_verified,
                "reason": "No eligible level has an upper intrusion bound within the risk ceiling."}
    choice = max(feasible, key=lambda item: (item.engagement_lower, -item.level))
    return {
        "status": "recommended", "recommended_level": choice.level,
        "level_name": LEVELS[choice.level], "estimate": asdict(choice),
        "eligible_levels": sorted(allowed_levels),
        "consent_verified": consent_verified,
        "risk_ceiling": max_intrusion_risk,
        "reason": "Highest lower-bound engagement among eligible levels that pass the upper-bound intrusion ceiling.",
    }


def current_dataset_status() -> dict:
    """Return the honest decision state for the supplied 49C files."""
    return recommend([], eligible_levels={0}, max_intrusion_risk=1.0,
                     evidence={name: False for name in REQUIRED_EVIDENCE})
