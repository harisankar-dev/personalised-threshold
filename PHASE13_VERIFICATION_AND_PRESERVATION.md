# Phase 13 verification and preservation

**Starting state (11 November 2026):** clean `main` at `476460c2fb900eb8f1c31377a38d46f3bbf067b0`, matching the completed Phase 12 commit. A recoverable local tag, `phase13-start-2026-11-11`, points to that commit. No reset, force push or pre-existing user edit was discarded. Original research reports, datasets, models and saved results were not overwritten.

## Environment and commands

- Windows, Anaconda Python 3.14.6, Node 24.22.1, Tesseract.js 7.0.0, local `models/eng.traineddata`, Pillow 12.3.0. No system Tesseract executable was found. Image OCR remains local. Native `pyreadstat` is still blocked by Windows Application Control; the Phase 12 R 4.6.1 `foreign` test adapter was used without changing security settings.
- Full regression command: set `PYTHONPATH='phase12_validation/compat;.phase8_vendor'`, `PYTHONIOENCODING='utf-8'`, `PHASE12_AD_CSV='C:\Users\imhar\Downloads\Advertising Image Dataset for Visual Analysis.csv'`, `PHASE12_AD_ZIP='C:\Users\imhar\Downloads\ad_images.zip'`; then run `C:\ProgramData\anaconda3\python.exe -m unittest discover -q`.
- Pre-change: **93 tests, OK**. Post-change after implementation: **102 tests, OK** (nine new test methods; their subtests cover more cases). The frozen Phase 12 result file is unchanged. Its regression test now checks its source hashes and frozen inventory rather than falsely requiring the intentionally revised live rubric to reproduce an old score.
- `python -m phase9_research.preservation verify`: **604 checked, zero errors** after changes.
- `python -m phase13_validation.audit_overlap`: no exact SHA-256 or difference-hash-distance-≤5 collisions among 12 Phase 13 and 25 Phase 12 images.
- `python -m phase13_validation.evaluate development`, `... test`, `python -m phase13_validation.evaluate_roi`, and `python -m phase13_validation.summarize` produce the committed aggregate metrics; downloaded images and full OCR dumps are deliberately ignored by Git.
- After the first final scoring, code review independently found that generic “Enter your phone number” wording could be over-scored. A narrow synthetic-tested fix was made, then the same six images were rerun only as a regression check. Their phrase and cue outputs were identical; timing was refreshed. This second run is disclosed and does not create a new untouched holdout.
- The local app ran at `127.0.0.1:8765`. Local Chrome could reach it only when server/browser processes ran outside the managed network sandbox. The browser script used actual form interactions and uploads; it made no external ad upload.

## Real-browser checks

All **21/21** Chrome checks passed: clear English image, generated limited-time image, small text, photographic text, angled text, seller phone, seller email, viewer identity text, negated urgency, generic ad, blank image, poor image, mixed-language image, unknown source, unverified consent, affordable revision, unaffordable revision, invalid-budget recovery, user-entered positive scenario, 390px mobile layout, and a generic phone-entry instruction. Seven real ad files used in browser diagnostics were not treated as independent consumer-validation examples; the generated deadline/blank/poor images are functional fixtures. The 390px layout had no horizontal document overflow. Image reads with no matched cue abstained. OCR text, cue evidence, reason, tier, budget action and warning were inspected via browser-rendered UI and local API responses.

## Files changed or added

Product/dependency: `.gitignore`, `requirements.txt`, `ocr_ad.cjs`, `intrusive_ad_model.py`. No `stp_advisory.py`, compatibility module, audience contract, threshold engine, model artifact, dashboard or research source was edited.

Tests: `test_phase12_validation.py` (frozen-baseline test corrected for intentional version change) and new `test_phase13_validation.py` (seller/viewer, urgency, OCR and threshold checks).

Versioned reproducibility: `phase13_validation/real_ad_reference_v1.json`, `ocr_experiment.py`, `evaluate.py`, `evaluate_roi.py`, `audit_overlap.py`, `overlap_audit_v1.json`, `summarize.py`, `metrics_v1.json`, `browser_checks.cjs`. The reference contains short project-authored visible phrases, not original image files. Local source JPGs, generated test images, detailed OCR logs and browser transcripts are ignored by Git.

Reports: `PHASE13_ENGLISH_OCR_VALIDATION.md`, `PHASE13_IDENTIFIER_CONTEXT_REPAIR.md`, `PHASE13_URGENCY_CUE_REPAIR.md`, `PHASE13_FRESH_REAL_AD_EVALUATION.md`, `PHASE13_STP_AND_BUDGET_REGRESSION.md`, `PHASE13_PRODUCT_VALIDATION_SUMMARY.md`, this report, plus updates to `README.md`, `PROJECT_STATUS.md` and `CHANGELOG.md`.

## Release guard

Python `compileall`, Node `--check` for both changed JavaScript files, the final 102-test suite and the 604-file manifest verifier passed. The explicit staged path list was inspected; it contained no downloaded ad image, raw archive or detailed OCR dump. `git diff --cached --check` passed and `python -m phase10_research.staging_guard` found no restricted path. The final delivery commit SHA and pushed/working-tree state are recorded in the handoff response because a Git commit cannot contain its own SHA-1 identifier without changing it.
