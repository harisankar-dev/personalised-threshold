"""Verify Phase 6 edits did not alter preserved research inputs or artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "baselines/phase6-start-2026-11-07/sha256.json"
OUTPUT = ROOT / "results/phase6_preservation_audit.json"
EXPECTED_PRODUCT_EDITS = {
    "marketer_app.py", "phase5_repro_audit.py", "web/index.html", "web/app.js",
    "web/app.css", "PROJECT_STATUS.md", "CHANGELOG.md",
}


def verify() -> dict:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    matched, changed, missing = [], [], []
    for entry in entries:
        rel = entry["path"].replace("\\", "/")
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        (matched if digest == entry["sha256"] else changed).append(rel)
    unexpected = [rel for rel in changed if rel not in EXPECTED_PRODUCT_EDITS]
    if missing or unexpected:
        raise AssertionError(f"Preservation check failed: missing={missing}, unexpected_changes={unexpected}")
    replay = json.loads((ROOT / "results/phase6_repro_audit.json").read_text(encoding="utf-8"))
    if len(replay["experiments"]) != 7:
        raise AssertionError("Phase 6 research replay is incomplete")
    return {
        "version": "phase6_preservation_audit",
        "checkpoint": str(MANIFEST.relative_to(ROOT)),
        "manifest_entries": len(entries),
        "unchanged_entries": len(matched),
        "intentional_product_or_documentation_changes": sorted(changed),
        "unexpected_changes": unexpected,
        "missing_files": missing,
        "research_replays": sorted(replay["experiments"]),
        "conclusion": "Checkpointed research code, saved results, model artifacts and four selected original sources are unchanged.",
    }


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("Versioned preservation audit already exists")
    report = verify()
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
