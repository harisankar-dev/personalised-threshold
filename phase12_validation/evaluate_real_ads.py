"""Reproduce the frozen, small Tier B real-ad text cue audit.

The source CSV and image ZIP are downloaded from Mendeley Data by the reader
and are intentionally not committed. No model fitting or rule tuning occurs.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile

from intrusive_ad_model import REPAIR_ADVICE, classify


HERE = Path(__file__).resolve().parent
LABELS = HERE / "real_ad_labels_v1.json"
CUES = sorted(set(REPAIR_ADVICE) - {"broad_targeting"})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(success: int, trials: int) -> list[float] | None:
    if trials == 0:
        return None
    z = 1.959963984540054
    p = success / trials
    d = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / d
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / d
    return [round(centre - half, 4), round(centre + half, 4)]


def measures(c: Counter) -> dict:
    tp, fp, fn, tn = (c[k] for k in ("tp", "fp", "fn", "tn"))
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": precision, "recall": recall, "f1": f1,
            "precision_wilson_95": wilson(tp, tp + fp),
            "recall_wilson_95": wilson(tp, tp + fn)}


def evaluate(csv_path: Path, zip_path: Path) -> dict:
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    if sha(csv_path) != labels["csv_sha256"] or sha(zip_path) != labels["zip_sha256"]:
        raise ValueError("Source hashes differ from the frozen labels")
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        source = list(csv.DictReader(handle))
    if len(source) != 605 or [row["ad_image"] for row in source] != [f"ad{i}.jpg" for i in range(1, 606)]:
        raise ValueError("Source CSV order, shape, or image identifiers changed")
    with zipfile.ZipFile(zip_path) as archive:
        names = {x.filename for x in archive.infolist() if not x.is_dir()}
        if names != {f"Datasets/ad ({i}).jpg" for i in range(1, 606)}:
            raise ValueError("Source image inventory differs from the frozen audit")
        image_hashes = [hashlib.sha256(archive.read(f"Datasets/ad ({x['id']}).jpg")).hexdigest()
                        for x in labels["cases"]]
    if len(set(image_hashes)) != len(image_hashes):
        raise ValueError("Selected creatives contain an exact image duplicate")
    counts = {split: Counter() for split in ("development", "test")}
    by_cue = {split: defaultdict(Counter) for split in counts}
    errors = []
    exclusions = []
    selected_texts = []
    for case in labels["cases"]:
        text = source[case["id"] - 1]["text"].strip()
        selected_texts.append(text)
        if not case["assessable"]:
            exclusions.append({"id": case["id"], "reason": case["note"]})
            continue
        if case["split"] not in counts:
            raise ValueError("Invalid split")
        present = set(case["present"])
        ambiguous = set(case["ambiguous"])
        if (present | ambiguous) - set(CUES) or present & ambiguous:
            raise ValueError("Invalid or conflicting cue labels")
        predicted = {item["cue"] for item in classify(text)["evidence"]}
        for cue in CUES:
            if cue in ambiguous:
                continue
            state = ("tp" if cue in present and cue in predicted else
                     "fp" if cue in predicted else "fn" if cue in present else "tn")
            counts[case["split"]][state] += 1
            by_cue[case["split"]][cue][state] += 1
            if state in {"fp", "fn"}:
                errors.append({"id": case["id"], "split": case["split"],
                               "cue": cue, "error": state})
    if len(set(selected_texts)) != len(selected_texts):
        raise ValueError("Selected creatives contain exact duplicate extracted copy")
    return {
        "evaluation_tier": "B: single-project-annotator labels on real source ads",
        "source": labels["source"], "license_listing": labels["license_listing"],
        "source_csv_sha256": sha(csv_path), "source_zip_sha256": sha(zip_path),
        "labels_sha256": sha(LABELS), "n_source_rows": len(source),
        "n_selected": len(labels["cases"]),
        "n_by_split": dict(Counter(x["split"] for x in labels["cases"])),
        "n_assessable_by_split": dict(Counter(x["split"] for x in labels["cases"] if x["assessable"])),
        "n_unassessable": len(exclusions),
        "n_ambiguous_cue_instances": sum(len(x["ambiguous"]) for x in labels["cases"]),
        "excluded": exclusions,
        "by_split": {s: {"micro": measures(counts[s]),
                         "by_cue": {cue: measures(by_cue[s][cue]) for cue in CUES}}
                     for s in counts},
        "errors": errors,
        "limitations": ["Single annotator; no inter-rater reliability or consumer outcomes",
                        "Publisher-extracted CSV text is not an independent OCR transcription",
                        "English-dominant, non-random selected sample; cue positives are sparse",
                        "No ad-specific targeting declarations or product category metadata"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(evaluate(args.csv, args.zip), handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
