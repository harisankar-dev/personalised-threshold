"""Safely unpack and audit the three user-supplied public survey archives.

The archives are copied into secondary_data/user_supplied_2026-11-07/archives.
Extraction refuses path traversal, links, oversized payloads, and overwrites.
"""
from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parent
BASE = ROOT / "secondary_data/user_supplied_2026-11-07"
ARCHIVES = BASE / "archives"
EXTRACTED = BASE / "extracted"
RESULT = ROOT / "results/three_user_datasets_audit_v1.json"
SPECS = {
    "vietnam_privacy": ("vietnam_privacy.zip", "048a7d46c4674b0fd2b750a1db08796f7aa2c3e04294ccf6da2c54b2ac9cd815"),
    "genz_personalized_ads": ("genz_personalized_ads.zip", "fc735da45e4c9db77f26f3d0fdf4a591ac57d92630caa24f62a9e9116dceb1c2"),
    "romano_han_unsolicited_ads": ("romano_han_unsolicited_ads.zip", "6ad799159b8c2d215627fada893082ee21c936d022a148eebc8c2e2ff057a3dc"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_member_path(name: str, destination: Path) -> Path:
    normalized = name.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if not parts or normalized.startswith("/") or any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ValueError(f"Unsafe ZIP path: {name!r}")
    root = destination.resolve()
    target = root.joinpath(*parts).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"ZIP member escapes extraction directory: {name!r}")
    return target


def extract_one(archive: Path, destination: Path) -> list[Path]:
    if destination.exists():
        raise FileExistsError(f"Extraction directory already exists: {destination}")
    planned = []
    with ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError(f"Corrupt ZIP: {archive}")
        files = [item for item in bundle.infolist() if not item.is_dir()]
        if sum(item.file_size for item in files) > 20_000_000:
            raise ValueError("Archive exceeds the 20 MB uncompressed audit limit")
        for item in files:
            if stat.S_IFMT(item.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError("ZIP links are not permitted")
            planned.append((item, safe_member_path(item.filename, destination)))
        if len({str(target).lower() for _, target in planned}) != len(planned):
            raise ValueError("Archive has duplicate destination paths")
        destination.mkdir(parents=True)
        for item, target in planned:
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(item) as source, target.open("xb") as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
    return [target for _, target in planned]


def data_quality(path: Path) -> dict:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, encoding="utf-8-sig")
    elif path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path)
    elif path.suffix.lower() == ".sav":
        import pyreadstat
        df, _ = pyreadstat.read_sav(path, apply_value_formats=False)
    else:
        raise ValueError(f"Not a data table: {path}")
    return {"rows": len(df), "columns": list(df.columns),
            "missing_cells": int(df.isna().sum().sum()),
            "full_duplicate_rows": int(df.duplicated().sum()),
            "column_missing_counts": {column: int(count) for column, count in df.isna().sum().items() if count}}


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("Versioned ZIP audit exists; preserve before a deliberate rerun")
    output = {"version": "three_user_datasets_audit_v1", "archives": {}}
    for dataset, (filename, expected) in SPECS.items():
        archive = ARCHIVES / filename
        if sha256(archive) != expected:
            raise ValueError(f"User ZIP checksum changed: {filename}")
        files = extract_one(archive, EXTRACTED / dataset)
        entries = []
        for path in files:
            counterpart = ROOT / "try these dataset" / path.name
            digest = sha256(path)
            entries.append({"relative_file": str(path.relative_to(ROOT)), "sha256": digest,
                            "local_counterpart": str(counterpart.relative_to(ROOT)) if counterpart.exists() else None,
                            "byte_identical_to_existing_local_file": counterpart.exists() and digest == sha256(counterpart),
                            "data_quality": data_quality(path) if path.suffix.lower() in {".csv", ".xlsx", ".sav"} else None})
        output["archives"][dataset] = {"archive": str(archive.relative_to(ROOT)),
                                       "archive_sha256": expected, "files": entries}
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({name: {"files": len(item["files"]),
                              "all_exact_duplicates": all(f["byte_identical_to_existing_local_file"] for f in item["files"]),
                              "tables": [f["data_quality"]["rows"] for f in item["files"] if f["data_quality"]]}
                      for name, item in output["archives"].items()}, indent=2))


if __name__ == "__main__":
    main()
