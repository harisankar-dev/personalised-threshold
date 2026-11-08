"""Diagnostic audit on external ad opinions; NOT intrusion-model validation.

The UW labels are clickbait, deceptive, and manipulative opinions, not direct
personalization-intrusion ratings. A fixed high/low sample is used only to
expose creative-screen coverage gaps. Do not tune the rubric on this output.
"""
from __future__ import annotations

import csv
import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from intrusive_ad_model import predict


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "secondary_data" / "chi-bad-ads-data"
OUT = ROOT / "results"
SEED = 49
SAMPLE_PER_GROUP = 30


def run_one(item: dict) -> dict:
    image = SOURCE / "screenshots" / f'{item["ad_id"]}.webp'
    result = predict(image=image)
    return {
        "ad_id": item["ad_id"], "opinion_group": item["opinion_group"],
        "max_problematic_label_share": round(item["max_problematic_label_share"], 4),
        "tier": result["tier"], "score": result["score_out_of_10"],
        "matched_cues": ";".join(x["cue"] for x in result["evidence"]),
        "ocr_confidence": result["ocr_confidence"],
        "ocr_characters": len(result["ocr_text"] or ""),
    }


def main() -> None:
    with (SOURCE / "data" / "opinion_label_dist_norm.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["max_problematic_label_share"] = max(
            float(row[name]) for name in ("clickbait", "deceptive", "manipulative")
        )
    high = [r for r in rows if r["max_problematic_label_share"] >= .5]
    low = [r for r in rows if r["max_problematic_label_share"] <= .1]
    rng = random.Random(SEED)
    selected = []
    for group_name, pool in (("high_opinion_concern", high), ("low_opinion_concern", low)):
        for row in rng.sample(pool, min(SAMPLE_PER_GROUP, len(pool))):
            row["opinion_group"] = group_name
            selected.append(row)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run_one, selected))
    OUT.mkdir(exist_ok=True)
    with (OUT / "external_creative_cases.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    summary = {
        "source": "https://github.com/eric-zeng/chi-bad-ads-data",
        "seed": SEED, "sample_per_group": SAMPLE_PER_GROUP,
        "label_definition": "Maximum annotator share for clickbait, deceptive, or manipulative",
        "group_thresholds": {"high": ">= 0.5", "low": "<= 0.1"},
        "warning": "Opinion groups are not direct personalization-intrusion labels; these counts are coverage diagnostics, not classification accuracy.",
        "groups": {},
    }
    for group_name in ("high_opinion_concern", "low_opinion_concern"):
        group = [r for r in results if r["opinion_group"] == group_name]
        summary["groups"][group_name] = {
            "n": len(group),
            "low": sum(r["tier"] == "low_intrusive" for r in group),
            "moderate": sum(r["tier"] == "moderate_intrusive" for r in group),
            "high": sum(r["tier"] == "high_intrusive" for r in group),
            "needs_review": sum(r["tier"] == "needs_review" for r in group),
            "no_ocr_text": sum(r["ocr_characters"] == 0 for r in group),
        }
    (OUT / "external_creative_audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["groups"], indent=2))


if __name__ == "__main__":
    main()
