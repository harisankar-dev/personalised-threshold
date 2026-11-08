# Changelog

## 6 November 2026 — Phase 4 secondary-data validation (app remains 0.1.0)

- Saved a start-of-phase checkpoint and SHA-256 manifest before changing code or results.
- Added a separately trained and calibrated survey uncertainty experiment. Its reused-holdout 90% two-sided interval covers 149/167 respondents, but covers only 5/10 below-neutral respondents; the one-sided upper bound misses six high-intrusion respondents at the agreement boundary. Kept this model research-only.
- Downloaded and audited a CC0 1,511-person independent web-ad intrusion survey. A separate regularized model improves held-out MAE from 0.955 (training-mean baseline) to 0.840 but has MAE 2.528 in the 26-person negative-intrusion segment. Did not merge survey respondents or connect the model to the app.
- Added `PHASE4_SECONDARY_DATA_REPORT.md`, two versioned experiment scripts/results/models, and focused tests. Public treatment-data leads still do not verify all five 49-C levels with intrusion and engagement; the threshold engine remains `insufficient_evidence`.

## 6 November 2026 — Phase 3 validation experiment (app remains 0.1.0)

- Reproduced V1 source hashes, 670/167 split, coefficients, and metrics exactly; saved a checksum manifest and recoverable V1/app checkpoint in `baselines/survey-phase-v1-2026-11-06/`.
- Audited questionnaire wording and construct overlap, then ran feature ablations, training-only V2 selection, held-out error and false-reassurance analysis, uncertainty estimates, subgroup checks, and split sensitivity. The small V2 MAE gain over V1 is uncertain and false reassurance at the agreement boundary worsened, so V2 remains a separate research artifact.
- Verified and audited three public experiment workbooks. Their conditions and outcomes cannot identify the project's five-level personalization/intrusion threshold. Kept the threshold decision at `insufficient_evidence` and left the app unchanged.
- Added `SURVEY_PHASE_V2_REPORT.md`, `survey_phase_v2.py`, `external_dataset_audit_v1.py`, versioned results/model files, and focused tests.

## 6 November 2026 — independent consumer-survey phase (app remains 0.1.0)

- Located direct 1–7 intrusiveness measurements in an 837-person secondary survey and checked their item mapping against the published data descriptor.
- Added `survey_phase_v1.py`, a versioned respondent-level ridge experiment with train-only scaling, an exact-answer-grouped holdout, baseline and ablation comparisons, calibration check, and bootstrap uncertainty. Preserved the source and the existing model.
- Audited the Gen Z personalized-ad workbook and reported construct associations without interpreting undocumented click/purchase response codes.
- Documented the secondary-data inventory, variable mapping, model limits, and next research requirements in `SECONDARY_SURVEY_PHASE_V1.md`; updated status and model documentation and added a scope note to the earlier manuscript to distinguish general survey ratings from ad-level intrusion screening.

## 6 November 2026 — isolated Criteo benchmark (app remains 0.1.0)

- Audited the complete Criteo Uplift source and retained a checksum-verified, untouched download plus a fixed 200,000-row sample.
- Trained binary ad-treatment visit models on Criteo alone. Preserved the failed undamped fit; the corrected damped logistic model beat constant-rate visit baselines on held-out data.
- Added an exact-feature-vector held-out split and bootstrap uplift check. The uplift-gain interval includes zero, so no uplift or personalization claim was added to the app.
- Documented source suitability, leakage controls, performance, uncertainty, reuse license, and limits in `CRITEO_UPLIFT_REPORT.md`.

## 0.1.0 — 6 November 2026

First formal version. The prior workspace had no declared release number.

- Preserved a checksum-verified snapshot of the unversioned analysis and creative screen in `baselines/unversioned-2026-11-06/`.
- Added `threshold_engine.py`, which requires valid engagement outcomes, direct intrusion labels, per-level exposure variation, and held-out validation before recommending a personalization level.
- Made verified consent, level eligibility, and the upper intrusion-risk bound hard constraints in the decision contract; current supplied data return `insufficient_evidence`.
- Exposed model version and threshold status in the local app while preserving creative-screen tier and score response fields.
- Documented source fields, data gaps, secondary-label requirements, model/evaluation plan, dashboard scope, and risks in `UPGRADE_V0_1_0.md`.
- Added pinned Python and OCR dependency manifests and decision-logic tests.
- Ran a fixed 60-image external opinion-label diagnostic; preserved pre/post results. Changed zero-cue image output from low to `needs_review` because OCR-only inspection cannot support a low-risk conclusion.

No real intrusiveness predictor or policy lift was trained or estimated in this release.
