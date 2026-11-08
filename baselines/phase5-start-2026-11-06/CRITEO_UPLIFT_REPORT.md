# Criteo Uplift: isolated secondary-data benchmark

**Date:** 6 November 2026  
**Status:** exploratory experiment; not connected to the 49-C marketer app or five-level decision engine

## Why this dataset was considered

The [Criteo Uplift dataset](https://huggingface.co/datasets/criteo/criteo-uplift) records a binary advertising treatment, visits, and conversions from incrementality tests. It is suitable for testing whether a model can rank users by a *visit response difference* between ad targeting and control. It does **not** contain ad text or images, perceived intrusiveness, consent, privacy preference, or levels 0–4 of personalization. Its anonymized features have no join key to the 49-C files. Criteo also says the original trials were non-uniformly subsampled, so the benchmark's rates must not be presented as the original population's advertising effect.

The publisher's card prose mentions 25 million rows and 11 features, while the actual current file, key figures, and schema specify 13,979,592 rows and 12 features (`f0`–`f11`). This experiment uses the verified file, not the inconsistent prose. The dataset is licensed CC BY-NC-SA 4.0; check that license before external or commercial reuse.

## Source audit and preparation

- Source: `secondary_data/criteo-uplift/criteo-research-uplift-v2.1.csv.gz` (311,422,618 compressed bytes), SHA-256 `2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc`.
- Full-file audit: 13,979,592 rows; no missing values in the 16 published columns. Detailed treatment/outcome counts are in `results/criteo_source_audit.json`.
- Selected 200,000 row indices uniformly without replacement across the full source with seed 49. The untouched source remains separate from the 49-C CSV files.
- Predictor list: only anonymized pre-treatment fields `f0`–`f11`. `treatment`, `visit`, and `conversion` are assignments/outcomes, and `exposure` is post-assignment, so none enter the predictor matrix. Scaling was learned from training rows only.

## Model and validation

Two separate L2-regularized logistic regressions predict visit probability under control and treatment. Their difference is a candidate uplift ranking. A damped Newton optimizer was needed: the first undamped fit diverged and collapsed to constant predictions. Its original failed artifacts are retained as `models/criteo_visit_uplift_v1.npz` and `results/criteo_visit_uplift.json`; they are **not** a valid result.

The corrected random-row split is saved as v2. The more conservative v3 split holds out complete, exact 12-feature vectors, so no identical vector occurs in both partitions. There is no user identifier, so this cannot guarantee a user-disjoint split. The v3 split contains 160,017 training rows and 39,983 test rows. The model was not tuned on the holdout.

| Held-out v3 visit metric | Constant rate | Two-arm logistic |
| --- | ---: | ---: |
| Control ROC-AUC | 0.500 | 0.945 |
| Control Brier score (lower is better) | 0.03717 | 0.02669 |
| Treatment ROC-AUC | 0.500 | 0.926 |
| Treatment Brier score (lower is better) | 0.04603 | 0.03309 |

**Visit prediction improved on this benchmark. Uplift ranking remains uncertain.** The observed v3 uplift AUUC gain over a random ranking is 0.00158; its 400-resample row-bootstrap 95% interval is **−0.00063 to 0.00378**, which includes zero. The top-ranked 10% have a 4.61-percentage-point treated-versus-control visit-rate difference, with a wide row-bootstrap interval of 0.54 to 7.80 points. These are benchmark-sample, conditional estimates, not a measured individual treatment effect or 49-C business outcome. The additional random-ranking check is in `results/criteo_uplift_validation_v3.json`.

The overall held-out treatment/control visit-rate difference is 0.97 percentage points in v3. Because Criteo deliberately subsampled the trials non-uniformly, do not interpret that number as the original trial's incrementality. The held-out conversion difference has a confidence interval crossing zero; conversion optimization is not supported by this experiment.

## Decision for 49-C

Keep Criteo as an independent example of secondary-data uplift modeling. It cannot train the three-class ad intrusiveness screen, calibrate the 0–10 intrusiveness score, or estimate which of the five personalization levels a marketer should use. The existing `threshold_engine.py` should continue to return `insufficient_evidence` for a personalized recommendation until a secondary dataset has valid per-level exposure and direct intrusiveness outcomes. No Criteo predictions or metrics are placed in the marketer UI.

## Reproduce

The preparation script is `criteo_uplift_prepare.py`; it checks the source checksum and refuses to overwrite existing outputs. `criteo_visit_uplift.py --split feature-group` creates the v3 model and result, and `criteo_uplift_validation.py` creates the uncertainty checks. Output guards require archiving versioned files before deliberate reruns. The scripts require Python with NumPy and pandas. Run `python -m unittest discover -p 'test_*.py'` for regression checks.

Experiment files: `secondary_data/criteo-uplift/`, `criteo_uplift_prepare.py`, `criteo_visit_uplift.py`, `criteo_uplift_validation.py`, `test_criteo_uplift.py`, `models/criteo_visit_uplift_v1.npz`, `models/criteo_visit_uplift_v2.npz`, `models/criteo_visit_uplift_v3.npz`, and `results/criteo_*.json`. Existing 49-C source, model, and UI files were not changed for this experiment.
