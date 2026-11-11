# Core dataset resolution and model results

**49-C | 11 November 2026 | Decision: PARTIAL GO for local, research-only condition analysis; NO-GO for individual prediction, segmentation by privacy preference, or product recommendations.** Git was clean at `130e9b81fd3d3e9987d83e87ada3feaab1d41755` before the work. No original file, prior model, application component or five-level threshold was changed.

## Source, rights and privacy

The user supplied `C:\Users\imhar\Downloads\use this\replication`, identified by its README and R scripts as the [Verenkotte–Spann location-targeting replication](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216). The three supplied workbook SHA-256 hashes exactly match the previously attached OSF ZIP: Study 1 `a614b914d193bdb...`, Study 2 `3080faaf4dfde1e5...`, Study 3 `7e9886b90bb2ffa8...`. The supplied folder's README adds “Free to use for research and model training as long as ethical” to the original 1,202-byte replication README. This line and the user's explicit direction authorize **this local research run**, but are not an independently verified OSF dataset license or a grant for redistribution, commercial deployment, or retained person-level derivatives. The original ZIP has no license file; the [previous OSF metadata check](PHASE10_DATA_ELIGIBILITY_AND_PRIVACY_REPORT.md) recorded a null license. This distinction remains a material deployment limitation.

The workbooks include IP addresses, location coordinates, response/platform IDs, and other administrative fields. The new script selects only `Targ`, `Trans`, `PPI`, `PPR`, `PP`, and `ITC` for its analytical DataFrame; the spreadsheet reader may transiently parse other workbook cells locally. It writes only aggregates. No original or minimized respondent table, identifier, fitted model binary, or individual profile was copied into the repository, logs, or application. The attached source files remain in Downloads and were not uploaded or redownloaded.

## Measurement and design

| Study | Independent records | Assigned 2×2 conditions | Outcomes |
| --- | ---: | --- | --- |
| Study 1 | 409, with 409 distinct respondent IDs | No location targeting vs city targeting × disclosure absent/present; cell sizes 107/98/98/106 | `PPI` direct privacy intrusiveness, `PPR` personal relevance, `PP` perceived personalization, `ITC` click **intention**, all 1–7. |
| Study 2 | 401, with 401 distinct respondent IDs | Country vs city targeting × disclosure absent/present; cell sizes 100/100/100/101 | Same 1–7 measures. Two additional empty worksheet rows are not respondent records. |
| Study 3 | Four aggregate ad-set rows | Field targeting/disclosure combinations | Aggregate clicks/impressions; no link to a respondent's intrusion rating. Excluded from individual modelling. |

No platform ID overlaps between Studies 1 and 2. The pooled workbook reuses the experimental records; it is not independent validation. Core fields have no missing values in the 810 complete online-experiment records. The data contain **no measured pre-exposure privacy preference or ad-relevance profile** that could support the requested privacy/relevance segmentation or a personal discomfort forecast. `PP`, `PPR`, and `ITC` are post-exposure variables and were excluded as predictors of `PPI`. Demographics were excluded because the intended app cannot obtain a validated, permissioned matching consumer profile. A zero/one targeting code has different meaning across the two studies; no row-level pooling was performed. No condition maps to L2 behavioural targeting, L3 historical personalization, or L4 combined hyper-personalization.

## Frozen evaluation

`location_condition_research_v1.py` pins source hashes, validates condition codes and 1–7 outcome bounds, and analyzes the studies separately. Each uses a seeded 75/25 condition-stratified respondent split. The candidate is the **training-cell mean** for each of four randomized conditions; the baseline is the **global training mean**. Five-fold checks use the training portion only. There is no model search or test-set tuning. Paired respondent bootstraps (2,000 draws) quantify uncertainty in the held-out MAE difference; within-cell bootstraps describe mean uncertainty. Seeds are fixed in the script; aggregate JSON is saved in `results/location_condition_research_v1.json`.

| Direct `PPI` outcome | Holdout | Global-mean MAE / RMSE | Condition-mean MAE / RMSE | MAE gain, 95% bootstrap interval | Observed `PPI ≥ 5` predicted **below 5** |
| --- | ---: | ---: | ---: | --- | ---: |
| Study 1 | 103 | 1.389 / 1.667 | 1.302 / 1.541 | 0.087 [−0.005, 0.178] | **18/18** |
| Study 2 | 101 | 1.233 / 1.460 | 1.222 / 1.461 | 0.011 [−0.081, 0.098] | **11/11** |

The condition means offer a descriptive view of the experiment, but neither held-out MAE gain is clearly positive and the high-discomfort false-reassurance result is unacceptable for a person-level claim. The study-specific four-cell observed `PPI`, `PPR`, and `ITC` means and mean bootstrap intervals are in the aggregate result file. Their intervals concern **group means**, not calibrated individual predictions. `ITC` is stated intention, not a business-uplift or conversion label. No trade-off weight between disclosure, discomfort and relevance was inferred. Disclosure may also be an ethical or legal obligation, so these observations do not justify suppressing it to lower a score.

## Product decision and verification

- **Individual discomfort prediction:** research-only condition averages; no useful individual estimator or app feature was promoted.
- **Consumer segmentation:** existing unrelated survey profiles remain descriptive. These experiments cannot assign privacy/relevance profiles or estimate reliable segment-by-condition responses.
- **Personalization recommendations:** no study-specific optimum or L0–L4 recommendation was established. `threshold_engine.current_dataset_status()` remains `insufficient_evidence`.
- **Application:** no code or UI changes; existing OCR, upload, STP and budget features remain intact. Chrome testing of a new workflow was inapplicable because no workflow passed validation.
- **Tests:** full documented Phase 12 R-backed compatibility environment: `114` tests run, `113` passing, `1` skipped. The research script completed against the supplied local workbooks and wrote aggregate-only output. No native security control was bypassed.

**Files added:** `location_condition_research_v1.py`, `results/location_condition_research_v1.json`, and this report. **Remaining barrier:** an independently verified source-use grant for broader deployment and, scientifically, pre-exposure consumer characteristics plus robust external validation with acceptable high-discomfort error. The present experiment cannot validate a universal five-level personalization threshold.
