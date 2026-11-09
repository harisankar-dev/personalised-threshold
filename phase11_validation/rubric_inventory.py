"""Export exact current regex patterns and weights for the Phase 11 audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from intrusive_ad_model import (
    COPY_CUES, DENIAL_BEFORE_CUE, DETAIL_PATTERN, EXCESSIVE_EXCLAMATION_PATTERN,
    NO_CONSENT_PATTERN, PRESSURE_CUES, TARGETING_CUES,
)


def inventory() -> dict:
    def rules(group):
        return [{"cue": name, "weight": weight, "regex": pattern.pattern}
                for name, weight, pattern in group]

    return {
        "source": "intrusive_ad_model.py",
        "label": "heuristic cue rubric; not calibrated to consumer ratings",
        "ad_copy": rules(COPY_CUES),
        "targeting_text": rules(TARGETING_CUES),
        "pressure": rules(PRESSURE_CUES),
        "derived": {
            "combined_signals": {"weight": 1, "condition": "at least two of browsing_history, purchase_history, approximate_location, precise_location, sensitive_personal_fact"},
            "specific_activity_detail": {"weight": 1, "condition": "browsing_history and a DETAIL_PATTERN match", "regex": DETAIL_PATTERN.pattern},
            "no_consent": {"weight": 2, "regex": NO_CONSENT_PATTERN.pattern},
            "excessive_exclamation": {"weight": 1, "condition": "at least two runs of three or more exclamation marks", "regex": EXCESSIVE_EXCLAMATION_PATTERN.pattern},
            "deny_scope_guard": {"condition": "skip a cue with a local explicit denial; inspect later matches", "regex": DENIAL_BEFORE_CUE.pattern},
        },
        "score": {"privacy_plus_pressure": True, "per_cue_once": True,
                  "display_cap": 10, "low": "sum < 2", "moderate": "2 <= sum < 6",
                  "high": "sum >= 6", "empty_or_unassessed_image": "needs_review"},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(inventory(), indent=2) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("refusing to overwrite existing inventory")
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
