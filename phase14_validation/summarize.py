"""Export aggregate-only OCR metrics without redistributing ad images or OCR dumps."""
import hashlib
import json
import statistics
from pathlib import Path

from phase14_validation.evaluate import DATA, RESULTS, ROOT, distance


def main() -> None:
    splits = {}
    for split in ("development", "test"):
        modes = {}
        for mode in ("baseline", "phase13", "revised"):
            rows = json.loads((RESULTS / f"{split}_{mode}_v1.json").read_text(encoding="utf-8"))["rows"]
            modes[mode] = {
                "n_creatives": len(rows),
                "region_micro_cer": round(sum(distance(r["reference"], r["roi_text"]) for r in rows) /
                                          sum(len(r["reference"]) for r in rows), 4),
                "region_micro_wer": round(sum(distance(r["reference"].split(), r["roi_text"].split()) for r in rows) /
                                          sum(len(r["reference"].split()) for r in rows), 4),
                "exact_full_image_phrases": sum(len(r["matched_phrases"]) for r in rows),
                "n_phrases": sum(r["n_phrases"] for r in rows),
                "median_full_seconds": round(statistics.median(r["full_seconds"] for r in rows), 3),
                "cases": [{"id": r["id"], "region_cer": r["cer"], "region_wer": r["wer"],
                           "exact_phrases": len(r["matched_phrases"]), "n_phrases": r["n_phrases"],
                           "full_seconds": r["full_seconds"]} for r in rows],
            }
        splits[split] = modes
    output = {"reference_file": str(DATA.relative_to(ROOT)),
              "reference_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
              "OCR_modes": {"baseline": "single original Tesseract.js pass",
                            "phase13": "frozen 139de17 Phase 13 append-all-lines OCR",
                            "revised": "Phase 14 single-transcript selection"},
              "warning": "OCR-only comparisons. All cue columns in local evaluation use current Phase 14 rules; they are not a cross-version cue comparison.",
              "splits": splits}
    (ROOT / "phase14_validation/metrics_v1.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
