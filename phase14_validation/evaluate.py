"""Versioned, split-aware OCR evaluation; source images/results remain local and ignored."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import time
import types
from pathlib import Path

from PIL import Image

from intrusive_ad_model import classify, ocr_image

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).with_name("frozen_reference_v1.json")
LOCAL = Path(__file__).with_name("local_source")
RESULTS = Path(__file__).with_name("local_results")
RESULTS.mkdir(exist_ok=True)
CUES = ("urgent_call_to_action", "direct_identifier", "explicit_surveillance")


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def distance(left, right) -> int:
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        new = [i]
        for j, b in enumerate(right, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = new
    return row[-1]


def old_ocr(path: Path) -> dict:
    run = subprocess.run(["node", str(ROOT / "ocr_ad.cjs"), str(path)],
                         capture_output=True, check=True, text=True, encoding="utf-8", timeout=45)
    return json.loads(run.stdout)


def phase13_ocr(path: Path) -> dict:
    source = subprocess.check_output(["git", "show", "139de17a3b8e83fdc688fb2f52a31e587cdcc3b8:intrusive_ad_model.py"],
                                     cwd=ROOT, text=True, encoding="utf-8")
    module = types.ModuleType("phase13_frozen")
    module.__file__ = str(ROOT / "intrusive_ad_model.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module.ocr_image(path)


def evaluate_one(case: dict, mode: str) -> dict:
    source = LOCAL / case["file"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != case["sha256"]:
        raise ValueError(f"Source hash changed: {case['id']}")
    region = LOCAL / (case["id"] + "_roi.png")
    with Image.open(source) as image:
        crop = image.crop(tuple(case["roi"]))
        crop.save(region)
    engine = {"baseline": old_ocr, "phase13": phase13_ocr, "revised": ocr_image}[mode]
    start = time.perf_counter()
    roi_result = engine(region)
    roi_time = time.perf_counter() - start
    start = time.perf_counter()
    full_result = engine(source)
    full_time = time.perf_counter() - start
    ref = normalize(case["roi_reference"])
    got = normalize(roi_result["text"])
    full = normalize(full_result["text"])
    matches = [p for p in case["phrases"] if normalize(p) in full]
    found = sorted({x["cue"] for x in classify(full_result["text"])["evidence"] if x["cue"] in CUES})
    return {"id": case["id"], "split": case["split"], "mode": mode,
            "cue_rule_version": "phase14_current_for_all_OCR_modes",
            "reference": ref, "roi_text": got, "full_text": full_result["text"],
            "cer": round(distance(ref, got) / len(ref), 4),
            "wer": round(distance(ref.split(), got.split()) / len(ref.split()), 4),
            "roi_seconds": round(roi_time, 3), "full_seconds": round(full_time, 3),
            "matched_phrases": matches, "n_phrases": len(case["phrases"]),
            "cue_present": case["cue_present"], "detected_cues": found,
            "confidence": full_result["confidence"],
            "enhanced_confidence": full_result.get("enhanced_confidence"),
            "warning": full_result.get("quality_warning"),
            "passes": full_result.get("passes", 1)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("split", choices=("development", "test"))
    parser.add_argument("mode", choices=("baseline", "phase13", "revised"))
    args = parser.parse_args()
    cases = [c for c in json.loads(DATA.read_text(encoding="utf-8"))["cases"] if c["split"] == args.split]
    rows = [evaluate_one(c, args.mode) for c in cases]
    target = RESULTS / f"{args.split}_{args.mode}_v1.json"
    target.write_text(json.dumps({"reference": str(DATA.relative_to(ROOT)), "rows": rows}, indent=2), encoding="utf-8")
    for row in rows:
        print(row["id"], row["mode"], "CER", row["cer"], "WER", row["wer"],
              "phrases", len(row["matched_phrases"]), "/", row["n_phrases"],
              "sec", row["full_seconds"], "cues", row["detected_cues"])
    print("median full seconds", statistics.median(row["full_seconds"] for row in rows))


if __name__ == "__main__":
    main()
