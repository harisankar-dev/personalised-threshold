# 49-C Phase 4: secondary-data improvement and validation

**Date:** 6 November 2026  
**Status:** completed research experiments. App version 0.1.0 and the five-level threshold engine are unchanged.

## Scope and preservation

This phase uses existing secondary data only. Before changes, 52 code, report, model, web, and small result files were copied to `baselines/phase4-start-2026-11-06/`; the SHA-256 manifest also records 15 original local dataset files. The project has no Git repository. Criteo, Survey V1, Survey V2, the marketer app, original datasets, and prior outputs were not overwritten. A preliminary uncertainty output was archived at `baselines/phase4-initial-conformal-prototype/` after an audit found that its calibration respondents had influenced the earlier V2 recipe selection. The final V3 selects its recipe entirely within its model-fit partition.

The scientific questions are narrower than the project title: Can the survey model express uncertainty reliably, and does an *independent* ad-intrusion questionnaire corroborate its broad measurement concerns? Neither survey contains an ad creative submitted by a marketer or an assigned 49-C personalization level.

## Data inventory and suitability

Local fields were inspected before searching online. “Intrusion” below means a **direct respondent rating**, not an inferred privacy or click label.

| Source | Observed unit and fields | Phase 4 decision |
| --- | --- | --- |
| Original [UPAD](https://zenodo.org/records/15717451) CSVs | User, ad, and recorded action tables. Earlier audit found 249,831 valid action joins but no non-actions/impression denominator, assigned personalization level, or direct intrusion rating. | Preserve event analysis; cannot estimate a five-level response curve. |
| [Romano–Han unsolicited-ads survey](https://data.mendeley.com/datasets/zcp5httw5c/1), local `.sav` | 837 respondents; six 1–7 direct intrusion items, privacy and benefit items, age/gender/frequency. No ad stimuli, randomized level, or linked engagement. CC BY 4.0. | Use for the versioned V3 uncertainty audit only. |
| [Gen Z personalized-ads survey](https://data.mendeley.com/datasets/czgx8b793m/1), local workbook | 296 respondents; perceived personalization, privacy, ad value, and purchase statements. No direct intrusion item or assigned treatment. CC BY 4.0. | Keep descriptive V1 findings separate; do not infer a threshold. |
| [Vietnam privacy/online-market survey](https://data.mendeley.com/datasets/2x8xnfbsfd/2), local CSV | 467 respondents, 32 fields, no missing cells; privacy practices, trust and buying-intention constructs. No ad stimulus or intrusion item. CC BY 4.0. | Exclude from intrusion/level training. |
| [UCI online shoppers](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset), local ZIP | 12,330 shopping sessions; 1,908 end in `Revenue=True`, no missing fields. No ad exposure, personalization, or intrusion. CC BY 4.0. | Purchase prediction is possible but would answer a different question; no 49-C integration. |
| [UW ad perceptions](https://github.com/eric-zeng/chi-bad-ads-data), local screenshots/labels | 500 ad screenshots, opinions from 1,025 annotators. Labels include clickbait, deceptive, and manipulative; no direct personalized-ad intrusion or level. | Existing 60-image diagnostic remains a coverage check, not an intrusion accuracy estimate. |
| [Criteo Uplift](https://huggingface.co/datasets/criteo/criteo-uplift), local archive | Binary ad targeting/control, visits and conversions, anonymized features; no intrusion, creative, consent, or levels 0–4. CC BY-NC-SA 4.0. | Preserve isolated uplift benchmark; do not transfer it into the app. |
| [Yu et al. Zenodo experiments](https://zenodo.org/records/22938743), three already-downloaded workbooks | 281, 305, 253 rows. Codebooks verify photo-format/regulatory-focus/parasocial conditions and purchase-intention fields, but no personalization treatment or intrusion/creepiness field. | Exclude, as documented in `results/phase3_external_dataset_audit_v1.json`. |
| **New:** [Redondo–Aznar ad-blocker survey](https://data.mendeley.com/datasets/89nk3kp8tg/1), downloaded workbook | 1,511 respondents, 32 fields, no missing cells or duplicate full records. Four direct web-ad intrusion items `ioa_1`–`ioa_4` on −3 to +3, ad attitudes and clutter, current/past blocker use. Publisher license **CC0 1.0**. Local SHA-256 `7da6b2c4c178b675ad69339bc6f3e18d7eef52e8e70e87ee7e4a79767c2c439d`. | Independent general-ad survey benchmark; keep separate from 49-C and Romano–Han respondents. |

The new file was downloaded from the publisher's file link and preserved as `secondary_data/research_candidates/redondo_aznar_ad_blockers_2018.xlsx`. Its `Data of ad blockers` sheet has the 1,511 × 32 structure and item names described on the publisher record. The source is publicly reusable under its stated CC0 license; this report retains attribution. No other public data were downloaded without verified suitable fields and rights.

### Additional treatment-data search

Searches of Mendeley Data, Zenodo, OSF-linked papers, and publication supplements found relevant **designs**, but no accessible respondent-by-ad file containing all five specified personalization treatments with direct intrusion and engagement outcomes. A [location-targeting/transparency study](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216) reports no/low/high targeting conditions and privacy-intrusion and click-intention outcomes, but no row-level data were verified in the accessed materials. A [political microtargeting transparency experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC10703312/) links an OSF deposit, but its randomized factor is **disclosure style**, and its reported outcomes are recognition, privacy concern and privacy-protection behavior rather than direct ad intrusion across five personalization levels. The [2026 personalized-imagery preprint](https://arxiv.org/abs/2609.12697) has three levels and exploratory creepiness; no accessible raw response table was verified in this search. An [AI recommendation privacy-invasion paper](https://www.mdpi.com/0718-1876/21/9/310) says participant-level data require an author request. We did not contact authors or convert published aggregate effects into invented records.

## Experiment 1: survey uncertainty with clean calibration

`survey_phase_v3_uncertainty.py` keeps the original 670/167 answer-vector-grouped split (seed 49). It divides the **670 original training responses** into 536 for model fitting/selection and 134 for calibration, with no exact answer vector across partitions. Five-fold grouped cross-validation compares the Phase 3 feature families and four ridge penalties **inside the 536 only**. It again selects the quadratic-privacy model with penalty 0.1 (fit-partition out-of-fold MAE 0.477). The 134 calibration outcomes set a finite-sample 90% absolute-residual quantile and a separate one-sided upper-residual quantile. Predictions and intervals are clipped to the questionnaire's original 1–7 bounds. The prior 167-person holdout is evaluated once in this script, but it was examined in V1/V2; the result is a **reused-holdout reliability audit**, not a new blind test.

| Reused holdout result | Value |
| --- | ---: |
| Point MAE / RMSE after fit/calibration split | 0.509 / 0.756 |
| Absolute calibration quantile | 1.171 points |
| Two-sided empirical coverage | 149/167 = 89.2% |
| Wilson 95% interval for observed coverage | 83.6%–93.1% |
| Median two-sided interval width | 2.342 points on a 1–7 scale |
| Below-neutral subgroup coverage | 5/10 = 50.0% |
| Agreement-with-intrusion subgroup coverage | 115/126 = 91.3% |
| One-sided upper-bound coverage | 143/167 = 85.6% |
| High-intrusion responses whose upper bound falls below agreement (5) | 6/126 |

The one-sided upper bound falls below 5 for 19 respondents; **six actually reported intrusion ≥5**. Thus even an upper-bound-based low-intrusion reassurance fails on some observed people. The under-neutral subgroup is small and poorly covered. Split-conformal *marginal* validity assumes exchangeable calibration and future responses; this convenience sample and previously examined holdout cannot establish future-person, subgroup, or ad-level validity. The intervals are uncertainty about respondent survey ratings, not a calibrated 0–10 ad-creative score. V3 is a distinct research artifact; its point MAE should not be presented as a new improvement over V2 because training counts differ and the test set has been reused.

The first prototype accidentally reused V2's selected recipe, which had been chosen with data later assigned to calibration. That prototype is archived. The final version reselects the recipe using only the 536 fit rows. A focused test changes all calibration and outer-test targets and confirms model-selection scores remain identical.

## Experiment 2: independent general web-ad intrusion survey

`ad_blockers_intrusion_v1.py` treats the arithmetic mean of four `ioa` items as the target on the publisher's **−3 to +3** scale. It uses no outcome item or source summary as a predictor. Full answer vectors are grouped because the file lacks respondent IDs; no exact vector crosses the 1,209/302 train/test split (seed 1049). Every scaler and ridge fit uses training rows only. Five grouped folds within training choose a ridge penalty from 0.1, 1, 10, 100 for three predeclared feature groups. The held-out 302 rows are then evaluated once. This is a separate dataset and a different intrusion construct: interruption of website activity by general ads.

| Feature group (same 302 holdout rows) | MAE | RMSE | R² |
| --- | ---: | ---: | ---: |
| Training-mean baseline | 0.955 | 1.247 | −0.002 |
| A: age and sex | 0.941 | 1.240 | 0.011 |
| B: A + ad knowledge, attitudes, pleasure, credibility, economic value | 0.872 | 1.155 | 0.142 |
| C: B + contemporaneous ad-clutter answers | **0.840** | **1.112** | **0.204** |

Training-only CV selected C, penalty 0.1, with out-of-fold MAE 0.784. The paired held-out bootstrap 95% interval for its **MAE gain over the training-mean baseline** is **0.066–0.165** points. Clutter and intrusion composites correlate 0.281 in all 1,511 responses; adding clutter improves same-survey prediction but can still reflect shared questionnaire method and related wording. The external survey does **not** validate the Romano–Han model: feature definitions, wording, response scales, and populations differ.

Extreme errors remain decisive. For the 26 held-out respondents with *negative* intrusion agreement, C's MAE is **2.528**, and its bias is +2.528. The 43 neutral-to-below-1 responses have MAE 0.931; the 233 with mean ≥1 have MAE 0.634. The model regresses strongly toward the prevalent positive ratings. Across the entire file, current ad-blocker users and nonusers are compared descriptively in the JSON result; blocker adoption could be a consequence of ad experience and was **not** used as a causal or deployable predictor. No threshold or ad-upload score is inferred from this model.

## Decision and reproducibility

There is still no verified dataset containing, for the **same respondent and ad**, an assigned and operationally defined Level 0–4 treatment, direct perceived intrusion, linked engagement including non-actions, and consent context. Criteo, both survey families, the original 49-C events, and the opinion-label screenshots remain separate. The app's content rubric and `threshold_engine.current_dataset_status()` are unchanged and continue to return `insufficient_evidence`. Neither new model is loaded by the app.

Use the bundled Python environment or install `requirements-research.txt`; on this workstation set `PYTHONPATH` to `.vendor` for pyreadstat. On a **fresh copy** of this project, run `python survey_phase_v3_uncertainty.py` and `python ad_blockers_intrusion_v1.py`. The scripts check source SHA-256 and refuse to overwrite versioned results or models. Run `python -m unittest discover -p 'test_*.py'`. Both Phase 4 JSON outputs and all saved model arrays were independently regenerated exactly in temporary directories. The checkpoint manifest confirms the original local datasets, V1/V2/Criteo results, models, app, and threshold engine still match their start-of-phase hashes.

**Next defensible step:** obtain a reusable secondary experiment with a real ad stimulus, specified treatment conditions, direct intrusion ratings, and linked engagement per participant. Existing three-level studies can inform an analysis design but cannot be relabeled as five measured levels. A fresh external cohort is also needed before interpreting survey-model interval coverage as prospective reliability.

## Final verification

`python -m unittest discover -p 'test_*.py'` passed **35/35 tests**, up from 29 at the start of Phase 4. The focused new tests check source grouping, training-only scaling, finite-sample calibration rank, and exclusion of calibration/outer-test targets from model selection. Both new experiments regenerated their JSON and saved model arrays exactly in temporary workspace directories. Of the 67 checkpointed source and project hashes, only the two intentionally updated documentation files (`CHANGELOG.md` and `PROJECT_STATUS.md`) changed. An in-process `/api/analyze` route check returned HTTP 200 and `insufficient_evidence`; no browser-level application test was performed in this phase.

### Files added or updated

- Checkpoints: `baselines/phase4-start-2026-11-06/` and archived calibration prototype at `baselines/phase4-initial-conformal-prototype/`.
- Downloaded source: `secondary_data/research_candidates/redondo_aznar_ad_blockers_2018.xlsx`.
- New experiments: `survey_phase_v3_uncertainty.py`, `ad_blockers_intrusion_v1.py`.
- Versioned outputs: `results/survey_phase_v3_uncertainty.json`, `models/unsolicited_intrusiveness_respondent_v3_calibrated.npz`, `results/ad_blockers_intrusion_v1.json`, `models/ad_blockers_intrusion_v1.npz`.
- New tests: `test_survey_phase_v3_uncertainty.py`, `test_ad_blockers_intrusion_v1.py`.
- Documentation: this report, updated `CHANGELOG.md`, updated `PROJECT_STATUS.md`.
