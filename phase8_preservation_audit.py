"""Read-only Phase 8 comparison against the pre-edit SHA-256 checkpoint."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKPOINT = ROOT / "baselines" / "phase8-start-2026-11-08"
EXPECTED_EDITED = {"README.md", "PROJECT_STATUS.md", "CHANGELOG.md", "marketer_app.py",
                   "stp_advisory.py", "web/index.html", "web/app.js", "web/app.css"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify() -> dict:
    manifest = json.loads((CHECKPOINT / "manifest.json").read_text(encoding="utf-8"))
    changed = []
    missing = []
    checkpoint_corruption = []
    for entry in manifest["files"]:
        rel = entry["path"]
        original = CHECKPOINT / rel
        current = ROOT / rel
        if not original.is_file() or digest(original) != entry["sha256"]:
            checkpoint_corruption.append(rel)
        if not current.is_file():
            missing.append(rel)
        elif digest(current) != entry["sha256"]:
            changed.append(rel)
    source_changed = []
    for entry in manifest["top_level_source_files"]:
        p = ROOT / entry["path"]
        if not p.is_file() or digest(p) != entry["sha256"]:
            source_changed.append(entry["path"])
    unexpected = sorted(set(changed) - EXPECTED_EDITED)
    return {"status": "preserved" if not (missing or checkpoint_corruption or source_changed or unexpected) else "review_required",
            "checkpoint_files": len(manifest["files"]),
            "unchanged_checkpoint_files": len(manifest["files"]) - len(changed) - len(missing),
            "expected_modified_files": sorted(set(changed) & EXPECTED_EDITED),
            "unexpected_modified_files": unexpected,
            "missing_files": missing,
            "checkpoint_corruption": checkpoint_corruption,
            "source_files_hashed": len(manifest["top_level_source_files"]),
            "source_files_changed": source_changed,
            "saved_model_and_result_changes": [p for p in changed if p.startswith(("models/", "results/"))]}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
