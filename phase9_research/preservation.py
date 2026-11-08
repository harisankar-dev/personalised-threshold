"""Record and verify SHA-256 hashes of pre-Phase-9 research inputs/artifacts.

The Git tag phase9-start-2026-11-08 is the recoverable code/report checkpoint.
This manifest checks original data, saved models, and saved results without
copying respondent records or loading them into memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("source_artifact_manifest.json")
ROOT_SOURCE_SUFFIXES = {".csv", ".gz", ".xlsx", ".xls", ".sav", ".zip", ".pdf", ".docx"}


def category(relative: str) -> str | None:
    normalized = relative.replace("\\", "/")
    if normalized.startswith(("secondary_data/", "try these dataset/")):
        return "source"
    if "/" not in normalized and Path(normalized).suffix.lower() in ROOT_SOURCE_SUFFIXES:
        return "source"
    if normalized.startswith("models/"):
        return "model"
    if normalized.startswith("results/"):
        return "result"
    return None


def tracked_research_files(root: Path = ROOT) -> list[tuple[str, str]]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    paths = [part.decode("utf-8") for part in raw.split(b"\0") if part]
    return [(path, kind) for path in paths if (kind := category(path))]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(root: Path = ROOT) -> dict:
    entries = []
    for relative, kind in tracked_research_files(root):
        path = root / relative
        entries.append({
            "path": relative.replace("\\", "/"),
            "category": kind,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    return {"checkpoint_git_tag": "phase9-start-2026-11-08", "entries": entries}


def verify(manifest: dict, root: Path = ROOT) -> list[str]:
    errors = []
    for entry in manifest["entries"]:
        path = root / entry["path"]
        if not path.is_file():
            errors.append(f"missing: {entry['path']}")
        elif path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            errors.append(f"changed: {entry['path']}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("write", "verify"))
    args = parser.parse_args()
    if args.action == "write":
        if MANIFEST.exists():
            parser.error(f"refusing to overwrite {MANIFEST}")
        manifest = build()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        counts = {kind: sum(e["category"] == kind for e in manifest["entries"])
                  for kind in ("source", "model", "result")}
        print(json.dumps({"manifest": str(MANIFEST), "counts": counts}))
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        errors = verify(manifest)
        print(json.dumps({"checked": len(manifest["entries"]), "errors": errors}))
        if errors:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
