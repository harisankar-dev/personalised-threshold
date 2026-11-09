"""Reproducible synthetic cue diagnostics, never consumer-intrusion accuracy."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from intrusive_ad_model import classify


HERE = Path(__file__).resolve().parent
CASES = HERE / "creative_cases_v1.json"


def _metrics(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def evaluate() -> dict:
    raw = CASES.read_bytes()
    fixture = json.loads(raw)
    counts = defaultdict(lambda: [0, 0, 0])
    kinds = defaultdict(lambda: [0, 0, 0])
    errors = []
    for case in fixture["cases"]:
        expected = set(case["expected"])
        result = classify(case["text"], case.get("targeting", ""))
        actual = {item["cue"] for item in result["evidence"]}
        for cue in expected | actual:
            slot = 0 if cue in expected and cue in actual else 1 if cue in actual else 2
            counts[cue][slot] += 1
            kinds[case["kind"]][slot] += 1
        if expected != actual:
            errors.append({"id": case["id"], "kind": case["kind"],
                           "false_positive": sorted(actual - expected),
                           "false_negative": sorted(expected - actual)})
    overall = [sum(value[i] for value in counts.values()) for i in range(3)]
    return {"fixture_version": fixture["version"], "fixture_sha256": hashlib.sha256(raw).hexdigest(),
            "label_basis": fixture["label_basis"], "n_cases": len(fixture["cases"]),
            "overall": _metrics(*overall),
            "by_cue": {key: _metrics(*value) for key, value in sorted(counts.items())},
            "by_creative_type": {key: _metrics(*value) for key, value in sorted(kinds.items())},
            "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(evaluate(), indent=2) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("refusing to overwrite existing evaluation output")
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
