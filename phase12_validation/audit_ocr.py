"""Observational English OCR audit on licensed real-ad screenshots.

The publisher CSV is a comparison field, not a verified character-accurate
transcription. Consequently this script does not calculate CER/WER.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

from PIL import Image

from intrusive_ad_model import classify, ocr_image


IDS = (12, 379, 389, 400, 403, 451, 469, 474, 484, 498)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    observations = []
    with zipfile.ZipFile(args.zip) as archive:
        for number in IDS:
            image = args.image_dir / f"ad_{number}.jpg"
            source_bytes = archive.read(f"Datasets/ad ({number}).jpg")
            if hashlib.sha256(image.read_bytes()).digest() != hashlib.sha256(source_bytes).digest():
                raise ValueError(f"Local source image {number} differs from publisher archive")
            width, height = Image.open(image).size
            ocr = ocr_image(image)
            publisher_text = rows[number - 1]["text"]
            observations.append({
                "id": number, "image_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "width": width, "height": height,
                "publisher_extracted_text": publisher_text,
                "local_english_ocr_text": ocr["text"],
                "local_ocr_confidence_unvalidated": ocr["confidence"],
                "cues_from_publisher_text": sorted(x["cue"] for x in classify(publisher_text)["evidence"]),
                "cues_from_local_ocr": sorted(x["cue"] for x in classify(ocr["text"])["evidence"]),
            })
    result = {
        "type": "observational OCR audit, no verified reference transcription or CER/WER",
        "source_csv_sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
        "source_zip_sha256": hashlib.sha256(args.zip.read_bytes()).hexdigest(),
        "n_images": len(observations), "ids": list(IDS),
        "observations": observations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
