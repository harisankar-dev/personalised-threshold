"""Offline-only Mode B schema gate; no customer-file endpoint or model.

Rows are inspected in memory and never returned or persisted. Permission flags
are declarations, not proof of legal eligibility or a basis for inference.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re


REQUIRED = {"anonymous_customer_id", "event_timestamp", "event_type", "behavioral_targeting_permitted"}
OPTIONAL = {"product_category", "campaign_id", "ad_id"}
EVENT_TYPES = {"product_view", "cart", "purchase", "ad_impression", "ad_click"}
ID_PATTERN = re.compile(r"[0-9a-f]{16,64}\Z")
CATEGORY_PATTERN = re.compile(r"[a-z][a-z0-9_]{1,39}\Z")
CODE_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
MAX_ROWS = 100_000


def validate_rows(rows: list[dict]) -> dict:
    """Fail closed; return only non-identifying validation counts."""
    if not isinstance(rows, list) or not rows or len(rows) > MAX_ROWS:
        raise ValueError("Provide 1–100000 event rows in memory.")
    seen = set()
    customer_ids = set()
    event_counts: Counter[str] = Counter()
    now = datetime.now(timezone.utc)
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or REQUIRED - row.keys() or row.keys() - (REQUIRED | OPTIONAL):
            raise ValueError(f"Row {index}: missing required fields or containing unapproved fields.")
        ident = row["anonymous_customer_id"]
        if not isinstance(ident, str) or not ID_PATTERN.fullmatch(ident):
            raise ValueError(f"Row {index}: use a 16–64 character hexadecimal pseudonym, not contact details.")
        if row["behavioral_targeting_permitted"] is not True:
            raise ValueError(f"Row {index}: processing stops when behavioural use is not explicitly permitted.")
        event = row["event_type"]
        if not isinstance(event, str) or event not in EVENT_TYPES:
            raise ValueError(f"Row {index}: unsupported event type.")
        stamp = row["event_timestamp"]
        if not isinstance(stamp, str):
            raise ValueError(f"Row {index}: timestamp must be ISO 8601 with a timezone.")
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Row {index}: invalid timestamp.") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.astimezone(timezone.utc) > now:
            raise ValueError(f"Row {index}: timestamp needs a timezone and cannot be in the future.")
        category = row.get("product_category")
        if category is not None and (not isinstance(category, str) or not CATEGORY_PATTERN.fullmatch(category)):
            raise ValueError(f"Row {index}: category must be a short controlled code.")
        if event in {"product_view", "cart", "purchase"} and category is None:
            raise ValueError(f"Row {index}: product events need a category.")
        for field in ("campaign_id", "ad_id"):
            value = row.get(field)
            if value is not None and (not isinstance(value, str) or not CODE_PATTERN.fullmatch(value)):
                raise ValueError(f"Row {index}: {field} must be a short opaque code.")
        if event in {"ad_impression", "ad_click"} and (not row.get("campaign_id") or not row.get("ad_id")):
            raise ValueError(f"Row {index}: ad events need campaign and ad identifiers.")
        fingerprint = (ident, parsed.astimezone(timezone.utc), event, category, row.get("campaign_id"), row.get("ad_id"))
        if fingerprint in seen:
            raise ValueError(f"Row {index}: indistinguishable duplicate event; supply a deduplicated source.")
        seen.add(fingerprint)
        customer_ids.add(ident)
        event_counts[event] += 1
    return {
        "status": "schema_validated_only",
        "rows": len(rows),
        "distinct_pseudonyms": len(customer_ids),
        "event_counts": dict(sorted(event_counts.items())),
        "individual_response_prediction": False,
        "data_retained": False,
        "note": "A permitted flag is a declared input, not verified consent. No audience targeting, category affinity or intrusion prediction is produced.",
    }
