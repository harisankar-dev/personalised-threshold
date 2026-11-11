"""Frozen Phase 13 real-ad comparison. Run test split once after implementation freeze."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import types
from pathlib import Path

from PIL import Image

from intrusive_ad_model import classify, ocr_image

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "phase13_validation/real_ad_reference_v1.json"
CUES = ("direct_identifier", "urgent_call_to_action")


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def distance(a: list[str] | str, b: list[str] | str) -> int:
    row = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        new = [i]
        for j, right in enumerate(b, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (left != right)))
        row = new
    return row[-1]


def baseline_model():
    source = subprocess.check_output(["git", "show", "476460c2fb900eb8f1c31377a38d46f3bbf067b0:intrusive_ad_model.py"],
                                     cwd=ROOT, text=True, encoding="utf-8")
    module = types.ModuleType("phase12_frozen_screen")
    module.__file__ = str(ROOT / "intrusive_ad_model.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module.classify


def source_image(ad_id: int) -> Path:
    path = ROOT / f"phase13_validation/local_source/ad_{ad_id}.jpg"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def old_ocr(path: Path) -> dict:
    result = subprocess.run(["node", str(ROOT / "ocr_ad.cjs"), str(path)], capture_output=True,
                            text=True, encoding="utf-8", timeout=45, check=True)
    return json.loads(result.stdout)


def analyze(case: dict, old_classify) -> dict:
    path = source_image(case["id"])
    with Image.open(path) as im:
        dimensions = list(im.size)
    results = {}
    for name, engine, classifier in (("baseline", old_ocr, old_classify), ("revised", ocr_image, classify)):
        start = time.perf_counter()
        try:
            ocr = engine(path)
            elapsed = round(time.perf_counter() - start, 3)
            transcript = ocr["text"]
            matched = [phrase for phrase in case["phrases"] if normalize(phrase) in normalize(transcript)]
            cues = sorted({e["cue"] for e in classifier(transcript)["evidence"] if e["cue"] in CUES})
            results[name] = {"seconds": elapsed, "failure": None, "text": transcript,
                             "confidence_unvalidated": ocr["confidence"],
                             "quality_warning": ocr.get("quality_warning"),
                             "severely_garbled": ocr.get("severely_garbled", False),
                             "passes": ocr.get("passes", 1), "matched_phrases": matched,
                             "detected_cues": cues, "empty": not transcript.strip()}
        except Exception as exc:
            results[name] = {"seconds": round(time.perf_counter() - start, 3),
                             "failure": f"{type(exc).__name__}: {exc}"}
    # Text-cue assessment uses visible project-authored English phrases, not
    # the publisher's unverified automatic OCR column.
    visible = "\n".join(case["phrases"])
    text_cues = {}
    for name, classifier in (("baseline", old_classify), ("revised", classify)):
        text_cues[name] = sorted({e["cue"] for e in classifier(visible)["evidence"] if e["cue"] in CUES})
    return {"id": case["id"], "split": case["split"], "dimensions": dimensions,
            "condition": case["condition"], "reference_phrases": case["phrases"],
            "cue_assessable": case.get("cue_assessable", True), "cue_present": case["cue_present"],
            "baseline": results["baseline"], "revised": results["revised"], "text_cues": text_cues}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("split", choices=["development", "test"])
    args = parser.parse_args()
    cases = [c for c in json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"] if c["split"] == args.split]
    classifier = baseline_model()
    rows = [analyze(case, classifier) for case in cases]
    output = {"split": args.split, "reference": str(REFERENCE.relative_to(ROOT)),
              "n_images": len(rows), "rows": rows}
    target = ROOT / f"phase13_validation/{args.split}_evaluation_v1.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        print(row["id"], row["dimensions"],
              "/".join(str(len(row[version].get("matched_phrases", []))) for version in ("baseline", "revised")),
              len(row["reference_phrases"]),
              "/".join(str(row[version].get("seconds")) for version in ("baseline", "revised")),
              row["revised"].get("quality_warning"), row["revised"].get("failure"))


if __name__ == "__main__":
    main()
