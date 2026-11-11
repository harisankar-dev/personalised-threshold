# Phase 14 verification and preservation

## Starting state and checkpoint

- Starting branch: `main`; clean at `139de17a3b8e83fdc688fb2f52a31e587cdcc3b8`.
- Recoverable local checkpoint tag: `phase14-start-2026-11-11` points to that commit. No prior commit/model/result was replaced.
- Pre-change full regression: 102 tests, 0 failures/errors/skips. Pre-change protected-artifact audit: `checked: 604`, `errors: []`.
- Approved test inputs: Salem CSV SHA-256 `cd5ad685312e6e365557166ad4b6d8e7a64825519c6edcb0044dfa0de7a8d0ca`; ad ZIP SHA-256 `b397f56216094a616a8e2b7a4b1af84afaf4155447d6f51801a9304406f8337c`.
- Frozen Phase 14 reference SHA-256 `d013a3379cf348ce4c122955bb1be6d6396296f5681373e150ca6474292d7250`. Individual image SHA-256 and ROI annotations are in that file. The four source images and complete OCR dumps are ignored, not committed.

## Changes and tests

Modified existing files: `.gitignore`, `intrusive_ad_model.py`, `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`. New files: `phase14_validation/frozen_reference_v1.json`, `phase14_validation/evaluate.py`, `phase14_validation/summarize.py`, `phase14_validation/metrics_v1.json`, `phase14_validation/browser_checks.cjs`, `test_phase14_validation.py`, and seven `PHASE14_*.md` reports. The original `ocr_ad.cjs`, app code, STP rules, threshold code, datasets, models and saved experiments were not edited.

Post-change full regression with `PYTHONPATH=phase12_validation/compat;.phase8_vendor`, `PYTHONIOENCODING=utf-8`, explicit original Salem CSV/ZIP paths and `C:\ProgramData\anaconda3\python.exe -m unittest discover -q`: **110 tests, 0 failures, 0 errors, 0 skips**. Windows Application Control still blocks native `pyreadstat`, so the documented R `foreign` test adapter was used; no security control was bypassed. Real local Chrome checks: **23 passed, 0 failed**, including 390 px layout and actual image uploads. The detailed local browser JSON is not committed because it contains extracted ad copy. Protected-file audit: **604/604 unchanged, 0 errors**. A restricted staging check must show no source JPG/PNG/archive, local OCR dump or prior result/model path staged before commit.

The final commit and push state are recorded in the Phase 14 handoff after `git rev-parse HEAD` and `git status --short`; a commit cannot contain its own SHA-1/SHA-256 identifier. Reproduce metrics by obtaining the source files at frozen hashes and running `python -m phase14_validation.evaluate development|test baseline|phase13|revised` followed by `python -m phase14_validation.summarize`. The test split was used once to decide whether to promote the OCR method; no later OCR selection or cue phrase was fitted to it. A subsequent code-review guard restored severe-garble abstention without changing selected OCR text.
