# Phase 12 — verification and preservation record

**Completed 10 November 2026, secondary data only.** The `main` working tree was clean at Phase 11 commit `a3955d2c4dcbbfcdc507162ce75ca1c8c6450856`. A local recoverable `phase12-start-2026-11-09` tag was placed on that commit **before edits**. There was no reset, force push, security-policy change, respondent-file processing or prior-artifact overwrite.

## Executed checks

| Check | Actual result |
| --- | --- |
| Pre-change full suite with `.phase8_vendor` and native `pyreadstat` | **90 run, 4 errors**, all blocked native `_readstat_parser` imports; no other test failure. |
| First full suite with explicit R-backed test-only adapter | **90 run, OK** before Phase 12 test additions. |
| Final full suite with `PHASE12_AD_CSV` and `PHASE12_AD_ZIP` pointing to publisher downloads | **93 run, OK; 0 failed, 0 errored, 0 skipped** in 8.108 seconds on the final rerun. This is the adapter runtime, not native-library recovery. |
| Focused product/privacy/API/threshold plus Phase 12 modules without source-file environment variables | **72 run, OK, 1 skipped** (source-file reproducibility check), hence 71 passed. |
| Frozen Phase 11 software cues | Recomputed 26 cases and matched `creative_after_v1.json` **exactly**: 18 TP, 1 FP, 2 FN, micro F1 0.9230769. |
| Frozen real-ad source/labels | Source hashes and 605-ID inventory checked, selected exact duplicates rejected, saved Tier B output re-evaluated exactly in full suite. |
| Phase 7 SAV alternate-reader fidelity | Original source hash check active; aggregate JSON matched the saved result **exactly**. V1 respondent result matched to `1e-8` numerical tolerance; exact floating representation differed. |
| Phase 9 SHA-256 preservation manifest | **604 files checked, zero missing or changed** after Phase 12 work. |
| Threshold | Direct call returned `status: insufficient_evidence`, `recommended_level: None`; all evidence gates remain missing. |
| Syntax | `node --check web/app.js`, `node --check ocr_ad.cjs`, and `py_compile` of the new Python modules/test passed. |
| API, STP and finance | Existing API, consent/source holds, A–E comparison, cost precision and budget tests are included in both full and focused suites; no app/advisory code changed. |
| Browser | **No new browser test**: no app, web UI or API code was edited. Phase 11's real-browser observations remain historical only. |

Final full-suite command:

```powershell
$env:PYTHONPATH = 'phase12_validation/compat;.phase8_vendor'
$env:PYTHONIOENCODING = 'utf-8'
$env:PHASE12_AD_CSV = 'C:\Users\imhar\Downloads\Advertising Image Dataset for Visual Analysis.csv'
$env:PHASE12_AD_ZIP = 'C:\Users\imhar\Downloads\ad_images.zip'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
```

## Exact file scope

**Modified:** `.gitignore`, `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`.

**Added:** `phase12_validation/compat/pyreadstat.py`, `phase12_validation/evaluate_real_ads.py`, `phase12_validation/audit_ocr.py`, `phase12_validation/real_ad_labels_v1.json`, `phase12_validation/real_ad_baseline_v1.json`, `phase12_validation/ocr_observations_v1.json`, `test_phase12_validation.py`, and seven `PHASE12_*.md` reports including this record.

**Unchanged:** `intrusive_ad_model.py`, `marketer_app.py`, `stp_advisory.py`, `phase8_compatibility.py`, `threshold_engine.py`, `web/`, Phase 11 fixtures, V1/V2/Criteo experiments, all saved models/results and original survey datasets. The downloaded source CSV/JPG archive and locally extracted sample images were **not staged**. The sample-image directory is Git-ignored. The full baseline and all reported metrics remain reproducible only with the attributed publisher download and matching hashes.

The restricted-file staging guard, staged-path list, whitespace check and push status are verified during the commit step. A Git commit cannot contain its own final SHA in this self-referential report; `git log -1` and the Phase 12 final handoff give the authoritative final SHA. The checkpoint tag retains the complete pre-change state.
