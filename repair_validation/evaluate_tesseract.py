"""Evaluate the production Tesseract.js path on frozen HierText splits."""
from __future__ import annotations

import argparse
import json
import re
import statistics
import time
import unicodedata
from pathlib import Path

from intrusive_ad_model import ocr_image


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(__file__).with_name("hiertext_reference_v1.json")
LOCAL = ROOT / "phase14_validation/local_source/hiertext_gate"
IMAGES = LOCAL / "candidate_extract/validation"
CROPS = LOCAL / "line_crops"
RAW = Path(__file__).with_name("local_results")
METRICS = Path(__file__).with_name("tesseract_metrics_v1.json")


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).strip().lower())


def search_normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize(value)).strip()


def edit_counts(reference, hypothesis) -> dict[str, int]:
    rows = [[(0, 0, 0, 0)] * (len(hypothesis) + 1) for _ in range(len(reference) + 1)]
    for left in range(1, len(reference) + 1):
        rows[left][0] = (left, 0, left, 0)
    for right in range(1, len(hypothesis) + 1):
        rows[0][right] = (right, right, 0, 0)
    for left in range(1, len(reference) + 1):
        for right in range(1, len(hypothesis) + 1):
            if reference[left - 1] == hypothesis[right - 1]:
                rows[left][right] = rows[left - 1][right - 1]
                continue
            deletion = rows[left - 1][right]
            insertion = rows[left][right - 1]
            substitution = rows[left - 1][right - 1]
            choices = [
                (deletion[0] + 1, deletion[1], deletion[2] + 1, deletion[3]),
                (insertion[0] + 1, insertion[1] + 1, insertion[2], insertion[3]),
                (substitution[0] + 1, substitution[1], substitution[2], substitution[3] + 1),
            ]
            rows[left][right] = min(choices)
    total, insertions, deletions, substitutions = rows[-1][-1]
    return {"distance": total, "insertions": insertions,
            "deletions": deletions, "substitutions": substitutions}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("split", choices=("development", "test"))
    args = parser.parse_args()
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    cases = [case for case in reference["cases"] if case["split"] == args.split]
    raw_rows = []
    character_totals = {key: 0 for key in ("distance", "insertions", "deletions", "substitutions")}
    word_totals = character_totals.copy()
    reference_characters = reference_words = empty_crops = failures = 0
    phrase_total = phrase_recovered = full_empty = 0
    crop_times, full_times = [], []
    case_summaries = []
    for case in cases:
        line_rows = []
        for line in case["lines"]:
            started = time.perf_counter()
            try:
                result = ocr_image(CROPS / line["local_crop"])
                elapsed = time.perf_counter() - started
                actual = normalize(result["text"])
                expected = normalize(line["reference"])
                chars = edit_counts(list(expected), list(actual))
                words = edit_counts(expected.split(), actual.split())
                for key in character_totals:
                    character_totals[key] += chars[key]
                    word_totals[key] += words[key]
                reference_characters += len(expected)
                reference_words += len(expected.split())
                empty_crops += not actual
                crop_times.append(elapsed)
                line_rows.append({"reference": line["reference"], "text": result["text"],
                                  "seconds": round(elapsed, 3), "characters": chars, "words": words,
                                  "empty": not actual, "warning": result.get("quality_warning")})
            except Exception as error:
                failures += 1
                line_rows.append({"reference": line["reference"], "failure": f"{type(error).__name__}: {error}"})
        started = time.perf_counter()
        try:
            full = ocr_image(IMAGES / f"{case['image_id']}.jpg")
            elapsed = time.perf_counter() - started
            full_times.append(elapsed)
            searchable = search_normalize(full["text"])
            recovered = [line["reference"] for line in case["lines"]
                         if search_normalize(line["reference"]) in searchable]
            phrase_total += len(case["lines"])
            phrase_recovered += len(recovered)
            full_empty += not full["text"].strip()
            full_row = {"text": full["text"], "seconds": round(elapsed, 3),
                        "recovered": recovered, "warning": full.get("quality_warning"),
                        "empty": not full["text"].strip()}
        except Exception as error:
            failures += 1
            phrase_total += len(case["lines"])
            full_row = {"failure": f"{type(error).__name__}: {error}"}
        raw_rows.append({"image_id": case["image_id"], "lines": line_rows, "full": full_row})
        case_summaries.append({"image_id": case["image_id"],
                               "phrases_recovered": len(full_row.get("recovered", [])),
                               "phrases_total": len(case["lines"]),
                               "full_seconds": full_row.get("seconds"),
                               "full_empty": full_row.get("empty")})
    aggregate = {
        "engine": "production Tesseract.js 7.0.0 through intrusive_ad_model.ocr_image",
        "reference": str(REFERENCE.relative_to(ROOT)), "reference_version": reference["version"],
        "split": args.split, "images": len(cases), "line_crops": sum(len(case["lines"]) for case in cases),
        "cer": round(character_totals["distance"] / reference_characters, 4),
        "wer": round(word_totals["distance"] / reference_words, 4),
        "character_insertions": character_totals["insertions"],
        "word_insertions": word_totals["insertions"],
        "phrase_recovery": phrase_recovered, "phrase_total": phrase_total,
        "empty_line_crops": empty_crops, "empty_full_images": full_empty,
        "failures": failures,
        "median_line_seconds": round(statistics.median(crop_times), 3),
        "median_full_seconds": round(statistics.median(full_times), 3),
        "cases": case_summaries,
    }
    RAW.mkdir(exist_ok=True)
    (RAW / f"tesseract_{args.split}_raw.json").write_text(
        json.dumps({"aggregate": aggregate, "rows": raw_rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    saved = json.loads(METRICS.read_text(encoding="utf-8")) if METRICS.exists() else {}
    saved[args.split] = aggregate
    METRICS.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
