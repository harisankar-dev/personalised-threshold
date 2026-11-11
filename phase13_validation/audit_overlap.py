"""Exact and perceptual overlap audit for the frozen Phase 13 ad IDs."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image

from phase13_validation.evaluate import ROOT, REFERENCE, source_image


def dhash(raw: bytes) -> int:
    with Image.open(io.BytesIO(raw)) as opened:
        pixels = list(opened.convert("L").resize((9, 8), Image.Resampling.LANCZOS).get_flattened_data())
    return sum((pixels[y * 9 + x] > pixels[y * 9 + x + 1]) << (y * 8 + x)
               for y in range(8) for x in range(8))


def main() -> None:
    old = json.loads((ROOT / "phase12_validation/real_ad_labels_v1.json").read_text(encoding="utf-8"))["cases"]
    new = json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"]
    archive = Path("C:/Users/imhar/Downloads/ad_images.zip")
    records = {}
    with zipfile.ZipFile(archive) as bundle:
        for case in old:
            raw = bundle.read(f"Datasets/ad ({case['id']}).jpg")
            records[f"phase12:{case['id']}"] = (hashlib.sha256(raw).hexdigest(), dhash(raw))
    for case in new:
        raw = source_image(case["id"]).read_bytes()
        records[f"phase13:{case['id']}"] = (hashlib.sha256(raw).hexdigest(), dhash(raw))
    collisions = []
    for key, (sha, perceptual) in records.items():
        if not key.startswith("phase13:"):
            continue
        for other, (other_sha, other_perceptual) in records.items():
            if other >= key or other == key:
                continue
            dist = (perceptual ^ other_perceptual).bit_count()
            if sha == other_sha or dist <= 5:
                collisions.append({"case": key, "other": other, "exact": sha == other_sha, "dhash_distance": dist})
    target = ROOT / "phase13_validation/overlap_audit_v1.json"
    target.write_text(json.dumps({"n_phase12": len(old), "n_phase13": len(new),
                                  "dhash_distance_flag_threshold": 5,
                                  "collisions": collisions}, indent=2), encoding="utf-8")
    print(target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
