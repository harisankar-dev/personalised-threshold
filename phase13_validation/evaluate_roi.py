"""CER/WER on predeclared, complete English headline regions only."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PIL import Image

from intrusive_ad_model import ocr_image
from phase13_validation.evaluate import ROOT, REFERENCE, distance, normalize, old_ocr, source_image


def main() -> None:
    rows = []
    for case in json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"]:
        if "roi" not in case:
            continue
        with tempfile.TemporaryDirectory(dir=ROOT / ".ocr_tmp") as temporary:
            cropped = Path(temporary) / "region.png"
            with Image.open(source_image(case["id"])) as image:
                image.crop(tuple(case["roi"])).save(cropped)
            reference = normalize(case["roi_reference"])
            runs = {}
            for name, engine in (("baseline", old_ocr), ("revised", ocr_image)):
                text = normalize(engine(cropped)["text"])
                runs[name] = {"text": text,
                              "cer": round(distance(reference, text) / len(reference), 4),
                              "wer": round(distance(reference.split(), text.split()) / len(reference.split()), 4)}
            rows.append({"id": case["id"], "split": case["split"], "roi": case["roi"],
                         "reference": reference, **runs})
    target = ROOT / "phase13_validation/roi_evaluation_v1.json"
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        print(row["id"], row["split"], row["baseline"]["cer"], row["revised"]["cer"],
              row["baseline"]["wer"], row["revised"]["wer"])


if __name__ == "__main__":
    main()
