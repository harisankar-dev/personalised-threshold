"""Verify downloaded Zenodo workbooks before assessing Phase 3 relevance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
FILES = {
    "zenodo_visual_presentation_dataset1.xlsx": "e877b822833df523f9e6105e51f5aa5e",
    "zenodo_visual_presentation_dataset2.xlsx": "661efc547efcfce413249f8282845398",
    "zenodo_visual_presentation_dataset3.xlsx": "0b6311e1ae991affcdf961b29c21dec3",
}
SOURCE = "https://zenodo.org/records/22938743"
RESULT = ROOT / "results/phase3_external_dataset_audit_v1.json"


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("Versioned external dataset audit already exists")
    datasets = []
    for name, expected_md5 in FILES.items():
        path = ROOT / "secondary_data/research_candidates" / name
        if not path.exists():
            raise FileNotFoundError(path)
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        if digest != expected_md5:
            raise ValueError(f"Publisher MD5 mismatch for {name}")
        workbook = pd.ExcelFile(path)
        if workbook.sheet_names != ["Data", "Codebook"]:
            raise ValueError(f"Unexpected sheets in {name}")
        data = pd.read_excel(workbook, "Data")
        codebook = pd.read_excel(workbook, "Codebook")
        columns = list(data.columns)
        if set(columns) != set(codebook["variable"]):
            raise ValueError(f"Data and codebook columns differ in {name}")
        documented_terms = " ".join(codebook.fillna("").astype(str).to_numpy().ravel()).lower()
        datasets.append({
            "file": str(path.relative_to(ROOT)), "publisher_md5": digest,
            "rows": len(data), "columns": len(columns),
            "condition_fields": [c for c in columns if c in
                                 {"photo_format", "regulatory_focus", "psr_condition"}],
            "has_direct_intrusion_or_creepiness_item": "intrus" in documented_terms or "creep" in documented_terms,
            "has_personalization_treatment": "personaliz" in documented_terms or "personalised" in documented_terms,
            "has_purchase_intention": "purchase_intention" in columns,
            "has_public_participant_id": "participant_id" in columns,
        })
    RESULT.write_text(json.dumps({"source": SOURCE, "datasets": datasets,
                                  "decision": "No personalization treatment or direct intrusion outcome; not integrated into 49-C."},
                                 indent=2), encoding="utf-8")
    print(json.dumps(datasets, indent=2))


if __name__ == "__main__":
    main()
