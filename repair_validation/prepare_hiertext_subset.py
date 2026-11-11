"""Freeze a small advertising-relevant HierText subset from official labels.

Source images and generated crops stay under the already ignored Phase 14 local
source directory. The versioned JSON contains only IDs, hashes and annotations.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "phase14_validation/local_source/hiertext_gate"
ANNOTATIONS = LOCAL / "validation.jsonl.gz"
IMAGES = LOCAL / "candidate_extract/validation"
CROPS = LOCAL / "line_crops"
OUTPUT = Path(__file__).with_name("hiertext_reference_v1.json")

ANNOTATION_SHA256 = "ce7085d8bf24c2f13df852715c34494e6748cafcabb4bfc7a6e2bb320f58d23a"
ARCHIVE_MD5 = "6a055aff4c749e43fcfbe9027d017904"

# Line strings are exact official HierText v1.0 annotations, selected before
# either OCR engine was run. Repeated strings resolve to the largest polygon.
CASES = {
    "development": {
        "11863e2d22a0dc6f": ["WE WON'T CRUMBLE", "FREE"],
        "30a7208a7004d7f4": ["Get your FREE Cingular ringtone", "Visit www.cingularringtone.com"],
        "37e0eb8fecffbbac": ["Distributors", "Run your own business without the usual risks..."],
        "38b9387bf8718119": ["Our Ceiling Prices", "WHICH WE OFFER YOU"],
        "4ec11f80acf62dd9": ["THIS AD IS WORTH $150.", "MEMBERS' OFFER ONLY"],
        "5dabe808217bfd83": ["HALF ORIGINAL PRICE", "MASSIVE SAVINGS"],
        "7a7d0f471fe900e2": ["ANGELICA'S CLEANING", "Your One Stop Cleaning Source for your home-house or business buildings!"],
        "8e7b2fac5ee696ce": ["FUn FACTORy ReUnIOn", "17 OCTOBeR 2009"],
        "95c199bdff1a4128": ["FREE", "Xbox Live Gold Trial"],
        "a018d36e4dea2053": ["SUBSCRIBE and SAVE", "SUBSCRIBE NOW! SAVE 25¢"],
        "dd97f087faa88397": ["ENTRÉE SPECIAL", "Sriracha Glazed Snapper"],
        "e1558ad38983d294": ["Don't try this", "with any other motor"],
    },
    "test": {
        "3025b88f005c3de4": ["35% Off!", "Buy today from"],
        "48904c0fff1c7fcb": ["Organic foods", "EA AND COFFEE SELECTION"],
        "4976c8479dc54b42": ["Here's why the new Inner Ford rides silent, solid and secure!", "Six or V-8-the going is great! Pick your GO... and love it!"],
        "58a0e272f66d774d": ["$5 Launch Special", "Socialize over creativity."],
        "6a45c292e1c487dc": ["For a very limited time we are offering the award-winning Ocean for only $99 when you sign", "Get an Ocean on Helio.com, by calling us at 888.88.HELIO or at any Helio location."],
        "7333961186f566fc": ["BUY ONE", "SPECIAL OFFER!"],
        "77ae21eab2f51710": ["stay fresh in Frigidaire", "Visit the nearest Frigidaire sales office or"],
        "992966bb8f545ecb": ["SPRING SPECIAL!", "FREE RENT"],
        "bdc508254b92ff40": ["INVEST IN YOUR", "Oregon Community Public Offering Law"],
        "d19b4b14a1d1e02b": ["sale limited time only", "limited time only"],
        "e6038450c7e33596": ["PROCLAIMERS", "GATES 6PM. VISIT THE MAGNERS FANTASTIC FOOD & BARS"],
        "f4711b48d0b52640": ["SIMMONS MATTRESS TRUCKLOAD SALE UNTIL", "UNBEATABLE VALUES!"],
    },
}


def digest(path: Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def polygon_area(line: dict) -> int:
    xs = [point[0] for point in line["vertices"]]
    ys = [point[1] for point in line["vertices"]]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def dhash(image: Image.Image) -> int:
    pixels = list(image.convert("L").resize((9, 8)).getdata())
    bits = 0
    for row in range(8):
        for column in range(8):
            bits = (bits << 1) | (pixels[row * 9 + column] > pixels[row * 9 + column + 1])
    return bits


def main() -> None:
    if digest(ANNOTATIONS) != ANNOTATION_SHA256:
        raise ValueError("Unexpected HierText validation annotation hash")
    data = json.loads(gzip.open(ANNOTATIONS, "rt", encoding="utf-8").read())
    annotations = {item["image_id"]: item for item in data["annotations"]}
    CROPS.mkdir(exist_ok=True)
    frozen = []
    image_hashes = set()
    perceptual = []
    for split, cases in CASES.items():
        for image_id, references in cases.items():
            source = IMAGES / f"{image_id}.jpg"
            item = annotations[image_id]
            source_hash = digest(source)
            if source_hash in image_hashes:
                raise ValueError(f"Duplicate image bytes: {image_id}")
            image_hashes.add(source_hash)
            lines = [line for paragraph in item["paragraphs"] for line in paragraph["lines"]
                     if line["legible"] and not line["handwritten"]]
            selected = []
            with Image.open(source) as image:
                perceptual.append((image_id, dhash(image)))
                for number, reference in enumerate(references, 1):
                    candidates = [line for line in lines if line["text"] == reference]
                    if not candidates:
                        raise ValueError(f"Reference missing for {image_id}: {reference}")
                    line = max(candidates, key=polygon_area)
                    xs = [point[0] for point in line["vertices"]]
                    ys = [point[1] for point in line["vertices"]]
                    pad = 6
                    box = [max(0, min(xs) - pad), max(0, min(ys) - pad),
                           min(image.width, max(xs) + pad), min(image.height, max(ys) + pad)]
                    crop_name = f"{image_id}_{number}.png"
                    image.crop(tuple(box)).save(CROPS / crop_name)
                    selected.append({"reference": reference, "vertices": line["vertices"],
                                     "crop_box": box, "local_crop": crop_name})
            frozen.append({"image_id": image_id, "split": split,
                           "width": item["image_width"], "height": item["image_height"],
                           "sha256": source_hash, "lines": selected})
    distances = []
    for index, (left_id, left_hash) in enumerate(perceptual):
        for right_id, right_hash in perceptual[index + 1:]:
            distances.append({"left": left_id, "right": right_id,
                              "hamming": (left_hash ^ right_hash).bit_count()})
    closest = min(distances, key=lambda row: row["hamming"])
    if closest["hamming"] <= 5:
        raise ValueError(f"Possible near duplicate: {closest}")
    output = {
        "version": "english_ocr_repair_hiertext_v1",
        "frozen_before_ocr": True,
        "source": "HierText v1.0 validation split (Open Images JPGs)",
        "source_url": "https://github.com/google-research-datasets/hiertext",
        "license": "CC BY-SA 4.0",
        "annotation_sha256": ANNOTATION_SHA256,
        "image_archive_md5": ARCHIVE_MD5,
        "selection": "24 visually inspected advertising-relevant images; exact official legible printed line labels",
        "metric_scope": "CER/WER on 48 complete bounded line crops; exact phrase recovery on 24 full images",
        "annotation_provenance": "Official HierText labels; no project-authored transcription",
        "closest_dhash_pair": closest,
        "cases": frozen,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}: {len(frozen)} images, {sum(len(row['lines']) for row in frozen)} lines")
    print("closest dHash pair", closest)


if __name__ == "__main__":
    main()
