"""Compare local OCR configurations on the frozen Phase 13 development split."""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "phase13_validation/real_ad_reference_v1.json").read_text(encoding="utf-8"))["cases"]


def image_path(ad_id: int) -> Path:
    matches = list((ROOT / "phase13_validation/local_source").glob(f"ad_{ad_id}.*"))
    if len(matches) != 1:
        raise FileNotFoundError(ad_id)
    return matches[0]


def variant(source: Path, choice: str, destination: Path) -> Path:
    if choice == "original":
        return source
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        if choice in {"gray2x", "color2x", "contrast2x"}:
            image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
        if choice in {"gray2x", "contrast2x"}:
            image = ImageOps.grayscale(image)
        if choice == "contrast2x":
            image = ImageOps.autocontrast(image, cutoff=1)
            image = ImageEnhance.Contrast(image).enhance(1.4)
        image.save(destination, format="PNG")
        return destination


def run_one(source: Path, choice: str, psm: str) -> dict:
    with tempfile.TemporaryDirectory(dir=ROOT / "phase13_validation/local_source") as temporary:
        path = variant(source, choice, Path(temporary) / "processed.png")
        start = time.perf_counter()
        result = subprocess.run(["node", str(ROOT / "ocr_ad.cjs"), str(path), psm],
                                capture_output=True, text=True, encoding="utf-8", timeout=45)
        return {"seconds": round(time.perf_counter() - start, 3), "exit_code": result.returncode,
                "result": json.loads(result.stdout) if result.returncode == 0 else {"error": result.stderr.strip()}}


def main() -> None:
    output = []
    for case in CASES:
        if case["split"] != "development":
            continue
        for choice, psm in [("original", "11"), ("color2x", "11"), ("gray2x", "11"),
                            ("contrast2x", "11"), ("color2x", "6")]:
            output.append({"id": case["id"], "variant": choice, "psm": psm,
                           **run_one(image_path(case["id"]), choice, psm)})
    (ROOT / "phase13_validation/dev_ocr_experiment_v1.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in output:
        print(row["id"], row["variant"], row["psm"], row["result"].get("confidence"),
              repr(row["result"].get("text", "")[:100].replace("\n", " ")))


if __name__ == "__main__":
    main()
