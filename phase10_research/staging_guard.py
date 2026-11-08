"""Reject restricted Phase 10 respondent files from the staged Git change."""

from __future__ import annotations

import subprocess


RESTRICTED_NAMES = frozenset({
    "study1_data.xlsx", "study2_data.xlsx", "study3_data.xlsx", "study1_2.xlsx",
})
RESTRICTED_DIRS = frozenset({"private_data", "derived_data", "restricted_models"})


def restricted_path(relative: str) -> bool:
    parts = relative.replace("\\", "/").lower().strip("/").split("/")
    return (
        parts[-1] in RESTRICTED_NAMES
        or (len(parts) > 2 and parts[0] == "phase10_research" and parts[1] in RESTRICTED_DIRS)
    )


def staged_restricted_paths() -> list[str]:
    raw = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"])
    paths = [part.decode("utf-8") for part in raw.split(b"\0") if part]
    return [path for path in paths if restricted_path(path)]


if __name__ == "__main__":
    blocked = staged_restricted_paths()
    if blocked:
        for path in blocked:
            print("restricted staged path: " + path)
        raise SystemExit(1)
    print("staging guard: no restricted Phase 10 paths staged")
