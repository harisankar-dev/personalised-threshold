"""Fail-closed, in-memory preparation for a future authorized OSF release.

This module does not download, read, write or model respondent data. Callers must
first supply reviewed, source-specific rights evidence; software flags alone are
not proof of permission. Tests use only synthetic fixtures.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Mapping, Sequence


STUDY_TARGETING = {
    1: {0: "no_location_targeting", 1: "city_location_targeting"},
    2: {0: "country_location_targeting", 1: "city_location_targeting"},
}
SOURCE_ID = "OSF zv8xy / Verenkotte-Spann location targeting"
TRANSPARENCY = {0: "no_disclosure", 1: "information_use_disclosure"}
RESEARCH_COLUMNS = ("Targ", "Trans", "PPI", "PPR", "PP", "ITC")
POST_EXPOSURE = frozenset(("PPI", "PPR", "PP", "ITC"))
PRELAUNCH_FEATURES = ("Targ", "Trans")
REQUIRED_RIGHTS = (
    "academic_analysis", "local_retention", "model_training",
    "derivative_artifacts", "publication", "privacy_review",
)


class EligibilityError(ValueError):
    """An intake condition is absent or invalid; do not process real data."""


def require_rights(record: Mapping[str, object]) -> None:
    """Require explicit, reviewed rights evidence for the entire intended workflow."""
    if record.get("source_id") != SOURCE_ID:
        raise EligibilityError("rights record does not identify this source")
    if record.get("evidence_type") not in {"dataset_license", "written_grant"}:
        raise EligibilityError("explicit source-specific rights evidence required")
    if not record.get("evidence_url_or_record") or not record.get("reviewed_by"):
        raise EligibilityError("rights citation and reviewer required")
    missing = [field for field in REQUIRED_RIGHTS if record.get(field) is not True]
    if missing:
        raise EligibilityError("unverified rights or privacy review: " + ", ".join(missing))


def _arm(value: object, label: str) -> int:
    if isinstance(value, bool) or value not in (0, 1):
        raise EligibilityError(f"{label} must be coded 0 or 1")
    return int(value)


def _rating(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise EligibilityError(f"{label} must be a 1–7 rating")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EligibilityError(f"{label} must be a 1–7 rating") from exc
    if not math.isfinite(number) or not 1 <= number <= 7:
        raise EligibilityError(f"{label} must be a finite 1–7 rating")
    return number


def validate_features(names: Sequence[str]) -> tuple[str, ...]:
    """Allow only assigned pre-exposure conditions in a PPI prediction task."""
    features = tuple(names)
    if len(features) != len(set(features)) or not features:
        raise EligibilityError("feature names must be unique and nonempty")
    forbidden = [name for name in features if name not in PRELAUNCH_FEATURES]
    if forbidden:
        raise EligibilityError("unverified or post-exposure feature: " + ", ".join(forbidden))
    return features


def minimize_rows(
    raw_rows: Sequence[Mapping[str, object]], *, study: int,
    rights: Mapping[str, object], respondent_key: str = "ResponseId",
) -> list[dict[str, float | int]]:
    """Copy six approved variables; never return an identifier or free text.

    The raw rows and respondent key may be handled only in an authorized isolated
    process. The key is used transiently to reject duplicate between-subject
    participants and is not copied to the output.
    """
    require_rights(rights)
    if study not in STUDY_TARGETING:
        raise EligibilityError("only Study 1 or Study 2 is supported")
    if not raw_rows:
        raise EligibilityError("no respondent rows")
    seen: set[str] = set()
    minimized = []
    for index, row in enumerate(raw_rows):
        key = row.get(respondent_key)
        if key is None or str(key).strip() == "":
            raise EligibilityError(f"missing respondent grouping key at row {index}")
        token = str(key)
        if token in seen:
            raise EligibilityError(f"duplicate respondent at row {index}")
        seen.add(token)
        try:
            clean = {
                "Targ": _arm(row.get("Targ"), "Targ"),
                "Trans": _arm(row.get("Trans"), "Trans"),
                "PPI": _rating(row.get("PPI"), "PPI"),
                "PPR": _rating(row.get("PPR"), "PPR"),
                "PP": _rating(row.get("PP"), "PP"),
                "ITC": _rating(row.get("ITC"), "ITC"),
            }
        except EligibilityError as exc:
            raise EligibilityError(f"invalid row {index}: {exc}") from exc
        minimized.append(clean)
    return minimized


def validate_minimized_rows(rows: Sequence[Mapping[str, object]]) -> None:
    """Reject added identifiers, quasi-identifiers, free text and missing fields."""
    if not rows:
        raise EligibilityError("no minimized rows")
    expected = set(RESEARCH_COLUMNS)
    for index, row in enumerate(rows):
        if set(row) != expected:
            raise EligibilityError(f"unexpected or missing minimized column at row {index}")
        _arm(row["Targ"], "Targ")
        _arm(row["Trans"], "Trans")
        for name in POST_EXPOSURE:
            _rating(row[name], name)


def treatment_label(study: int, targ: object, trans: object) -> tuple[str, str]:
    if study not in STUDY_TARGETING:
        raise EligibilityError("only Study 1 or Study 2 is supported")
    return STUDY_TARGETING[study][_arm(targ, "Targ")], TRANSPARENCY[_arm(trans, "Trans")]


def respondent_disjoint_split(
    rows: Sequence[Mapping[str, object]], respondent_keys: Sequence[str], *,
    test_fraction: float = 0.2, seed: int = 10,
) -> tuple[list[int], list[int]]:
    """Create treatment-cell-stratified indices without returning respondent IDs.

    Repeated observations stay together. A respondent observed in different
    treatment cells is rejected because the planned studies are between-subject.
    This is a partition helper, not a model fit or a held-out result.
    """
    if not rows or len(rows) != len(respondent_keys) or not 0 < test_fraction < 1:
        raise EligibilityError("invalid split inputs")
    cells: dict[tuple[int, int], dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    assigned: dict[str, tuple[int, int]] = {}
    for index, (row, key) in enumerate(zip(rows, respondent_keys)):
        if not key:
            raise EligibilityError("missing respondent grouping key")
        cell = (_arm(row.get("Targ"), "Targ"), _arm(row.get("Trans"), "Trans"))
        if key in assigned and assigned[key] != cell:
            raise EligibilityError("respondent crosses treatment cells")
        assigned[key] = cell
        cells[cell][key].append(index)
    rng = random.Random(seed)
    train, test = [], []
    for groups in cells.values():
        keys = sorted(groups)
        if len(keys) < 2:
            raise EligibilityError("each treatment cell needs at least two respondents")
        rng.shuffle(keys)
        n_test = min(len(keys) - 1, max(1, round(len(keys) * test_fraction)))
        test_keys = set(keys[:n_test])
        for key, indexes in groups.items():
            (test if key in test_keys else train).extend(indexes)
    return sorted(train), sorted(test)
