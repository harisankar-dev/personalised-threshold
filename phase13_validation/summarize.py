"""Publish aggregate Phase 13 metrics without redistributing ad images/OCR dumps."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from phase13_validation.evaluate import ROOT, CUES, distance


def split_metrics(split: str) -> dict:
    rows = json.loads((ROOT / f"phase13_validation/{split}_evaluation_v1.json").read_text(encoding="utf-8"))["rows"]
    result = {"images": len(rows), "reference_phrases": sum(len(r["reference_phrases"]) for r in rows)}
    for name in ("baseline", "revised"):
        result[name] = {
            "phrases_recovered": sum(len(r[name].get("matched_phrases", [])) for r in rows),
            "empty": sum(bool(r[name].get("empty")) for r in rows),
            "failures": sum(bool(r[name].get("failure")) for r in rows),
            "median_seconds": round(statistics.median(r[name]["seconds"] for r in rows), 3),
            "max_seconds": round(max(r[name]["seconds"] for r in rows), 3),
            "review_warnings": sum(bool(r[name].get("quality_warning")) for r in rows),
            "severely_garbled": sum(bool(r[name].get("severely_garbled")) for r in rows),
            "text_cue_matrix": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "image_cue_matrix": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
        }
        for row in rows:
            if not row["cue_assessable"]:
                continue
            truth = set(row["cue_present"])
            text_found = set(row["text_cues"][name])
            image_found = set(row[name].get("detected_cues", []))
            for cue in CUES:
                for label, found in (("text_cue_matrix", text_found), ("image_cue_matrix", image_found)):
                    key = ("tp" if cue in truth else "fp") if cue in found else ("fn" if cue in truth else "tn")
                    result[name][label][key] += 1
    return result


def roi_metrics() -> dict:
    rows = json.loads((ROOT / "phase13_validation/roi_evaluation_v1.json").read_text(encoding="utf-8"))
    result = {}
    for split in ("development", "test"):
        selected = [r for r in rows if r["split"] == split]
        result[split] = {"regions": len(selected), "ids": [r["id"] for r in selected]}
        for name in ("baseline", "revised"):
            chars = sum(len(r["reference"]) for r in selected)
            words = sum(len(r["reference"].split()) for r in selected)
            result[split][name] = {
                "cer_micro": round(sum(distance(r["reference"], r[name]["text"]) for r in selected) / chars, 4),
                "wer_micro": round(sum(distance(r["reference"].split(), r[name]["text"].split()) for r in selected) / words, 4),
                "by_id": {str(r["id"]): {"cer": r[name]["cer"], "wer": r[name]["wer"]} for r in selected},
            }
    return result


def main() -> None:
    browser = json.loads((ROOT / "phase13_validation/browser_results_v1.json").read_text(encoding="utf-8"))
    output = {"development": split_metrics("development"), "test": split_metrics("test"),
              "roi": roi_metrics(), "browser": {"checks": len(browser), "passed": sum(r["pass"] for r in browser)}}
    target = ROOT / "phase13_validation/metrics_v1.json"
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
