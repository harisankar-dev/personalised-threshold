# Phase 12 — SPSS regression-environment recovery

**10 November 2026.** The clean starting `main` commit was `a3955d2c4dcbbfcdc507162ce75ca1c8c6450856`; tag `phase12-start-2026-11-09` preserves it. Pre-change full suite: **90 run, 4 errors**. The affected tests were `test_direct_intrusion_items_are_the_target_only`, `test_answer_vector_groups_never_cross_partitions`, `test_cv_does_not_read_held_out_targets`, and `test_model_selection_excludes_calibration_and_outer_holdout_targets`. Each encountered `ImportError: DLL load failed while importing _readstat_parser: An Application Control policy has blocked this file.` The remaining 86 ran without failure. This reproduces Phase 11; its focused 69 passed historically, but Phase 11 did not have a full pass.

The Python runtime is `C:\ProgramData\anaconda3\python.exe`, Anaconda **3.14.6**, 64-bit AMD64; Node is **v24.22.1**. `.phase8_vendor` contains `pyreadstat` **1.3.7**, whose wheel tag `cp314-cp314-win_amd64` matches the interpreter ABI, so the error is not an obvious missing package or wrong architecture. Its `_readstat_parser.cp314-win_amd64.pyd` SHA-256 is `29E4485DBDA0238D774B49895C3FFE10373CFE664B848FF14BE4664D7FFAA725`; local package metadata names upstream [Roche/pyreadstat](https://github.com/Roche/pyreadstat) and Apache-2.0. Windows reports the module **NotSigned** and no Zone.Identifier stream was observed. Metadata and hash establish local identity, not publisher authenticity; the policy block remains authoritative. The Anaconda base lacks a separately approved pyreadstat; no extra Conda environment was found.

An installed **R 4.6.1** distribution has the existing `foreign` package. `foreign::read.spss(..., use.value.labels=FALSE, to.data.frame=TRUE)` read the original Romano–Han SAV as **837 × 27**, with the expected column order and first `I1` values `7,6,7,5,7,6`. A versioned test-only adapter at `phase12_validation/compat/pyreadstat.py` invokes that installed reader, emits raw numeric codes to in-memory CSV and returns a pandas frame to the existing callers. The original SAV, prior research code, results, models and blocked native binary remain untouched. This adapter is deliberately activated only by prepending its directory to `PYTHONPATH`; it rejects value-label formatting and is **not** a general pyreadstat or production replacement. No Windows policy or security setting was changed.

**Fidelity checks:** the existing SAV hash check in `phase7_segmentation.py` remained active. A fresh Phase 7 aggregate analysis using the alternate reader matched `results/phase7_segmentation_v1.json` **exactly** as a Python object, including respondent count, duplicate count, construct summaries, intervals and quadrant assignments. The Phase V1 respondent result matched its saved nested result to numerical tolerance `1e-8`, with only nonmaterial floating representation differences; an exact object equality check was false. The full four previously errored survey tests then executed normally. This supports this source and existing callers; it is not validation for arbitrary SAV files, encodings or metadata APIs.

## Commands and observed results

```powershell
$env:PYTHONPATH = '.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
# Before Phase 12 changes: 90 run, 4 errors (Windows Application Control).

$env:PYTHONPATH = 'phase12_validation/compat;.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
# After adapter, before three new Phase 12 tests: 90 run, OK.
```

The final full-suite command and count, plus focused checks, are in `PHASE12_VERIFICATION_AND_PRESERVATION.md`. Native pyreadstat remains blocked under the original command; **the recovered full-suite result is for the explicit R-backed compatibility environment only**. This is a policy-compliant alternative reader for the same source data, not a security bypass or a claim that the native package now loads.
