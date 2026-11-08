# 49-C Phase 3: respondent intrusiveness validation

**Date:** 6 November 2026  
**Status:** independent research experiment. The marketer app and five-level threshold engine remain at version 0.1.0.

## Objective and provenance

This phase tests whether the V1 respondent model's apparent accuracy survives a construct-overlap audit, feature ablations, training-only model selection, response-range error checks, and split sensitivity. It also searches for **secondary data** with observed personalization treatments and direct intrusion outcomes. No unrelated respondents were merged.

The source is the 837-person US social-media survey published by [Romano and Han (2022)](https://www.mdpi.com/2306-5729/7/10/138) and deposited at [Mendeley Data](https://data.mendeley.com/datasets/zcp5httw5c/1). Its six `I1`–`I6` responses agree with the published intrusion-item means. Respondents rated general ads based on previous online activity on a seven-point agreement scale; they did not rate ad creatives supplied to the 49-C app. The V1 source, script, model, and output hashes were checked and the 670/167 split, coefficients, and all reported metrics were reproduced exactly. A copy of V1 code, model, results, and unchanged app/threshold files, plus source hashes, is in `baselines/survey-phase-v1-2026-11-06/`. This project has no Git repository.

## Questionnaire and construct-overlap audit

The [published questionnaire](https://www.mdpi.com/2306-5729/7/10/138) asks whether ads based on past online activity feel *invasive, intrusive, interfering, disturbing, distracting,* and *forced* (`I1`–`I6`). Privacy items `PC1` and `PC3` explicitly ask about discomfort from sharing without permission and unwanted advertising. `PC2`, `PC4`, `PC5`, and `PC6` concern misuse, storage safety, and unauthorized sharing. The other candidate predictors are age, gender, social-media use frequency, and four perceived ad-benefit items. Avoidance responses and all `I` items remain outside the feature matrix. The target is solely the arithmetic mean of the six direct `I` items; the source's `ITV_mean` is an exact cross-check, never a predictor.

| Diagnostic from the same 837 responses | Result |
| --- | ---: |
| Privacy/intrusion composite Pearson correlation | 0.760 |
| Privacy/intrusion composite Spearman correlation | 0.793 |
| Mean absolute cross-item HTMT-style ratio | 0.830 |
| Cronbach alpha: intrusion / privacy / benefits | 0.906 / 0.921 / 0.948 |

Each privacy item correlates **0.628–0.662** with the intrusion-item mean. High internal consistency confirms that each item set moves together; it does not establish independent constructs or future predictive validity. The simultaneous self-report method and overlapping wording make privacy concern a **concurrent psychological proxy**, not an independent causal or pre-exposure signal available when a marketer uploads an ad. Removing the two most explicit discomfort/unwanted-ad items still leaves correlated contemporaneous privacy questions.

## Data preparation and validation

- Source SHA-256 is checked against V1 before modelling. The 837 source rows have no missing construct items; two exact duplicate answer vectors remain as possible distinct respondents and are kept together in the split.
- The **identical V1 holdout** is used for all fixed feature-set comparisons: 670 training and 167 held-out responses, seed 49. There is no respondent ID for stronger grouping.
- Training-only standardization and an unpenalized intercept are used. Predictions are clipped to the original 1–7 scale. The baseline is the training target mean.
- A separate five-fold grouped cross-validation **within the 670 training rows** compares linear ridge and one quadratic privacy term at penalties 0.1, 1, 10, and 100. The quadratic is `(privacy_mean − neutral 4)^2`. The candidate with lowest out-of-fold MAE is fixed before the 167-row holdout is scored. No test-set tuning is used.
- Simple ridge and one quadratic are appropriate for 837 rows. Random forests, boosting, and elastic net were not added because this phase's main risk is measurement overlap and very small low-intrusion counts, not model capacity.

### Feature ablation on the same holdout

All rows below use the **V1 ridge penalty 10** to isolate feature contribution. This table is diagnostic; it was not used to select V2.

| Predictors | MAE ↓ |
| --- | ---: |
| A: age, gender, social-media frequency | 0.796 |
| B: A + perceived ad benefits | 0.796 |
| C: B + all six privacy items' mean | 0.521 |
| C sensitivity: B + privacy mean excluding `PC1`, `PC3` | 0.558 |

The all-privacy block reduces held-out MAE by **0.275** points relative to B. Across 30 other seeded splits, its median MAE reduction is **0.373** (10th–90th percentile 0.308–0.406). Those split checks reuse the same survey and are sensitivity evidence, not independent validation. Benefits add almost nothing on the fixed holdout. The reduced privacy composite still carries shared survey-method and conceptual overlap.

## V1 versus training-selected V2

Training-only cross-validation selected a quadratic privacy ridge with penalty **0.1** (out-of-fold MAE **0.479**). The best linear-all candidate's out-of-fold MAE was **0.485**. V2 is stored separately and was **not** substituted for V1 in the app.

| Fixed 167-person holdout | MAE ↓ | RMSE ↓ | R² vs held-out mean |
| --- | ---: | ---: | ---: |
| Training-mean baseline | 0.815 | 1.028 | −0.066 |
| Original saved V1 ridge | 0.521 | 0.764 | 0.411 |
| Training-selected V2 quadratic ridge | **0.509** | **0.751** | **0.432** |

V2's MAE gain over V1 is **0.012** points. Its paired 2,000-resample held-out bootstrap 95% interval is **−0.003 to 0.028**, which includes no gain. V2's gain over the training-mean baseline has interval **0.206 to 0.407**. The model's mean prediction error is **−0.138**; residuals range from **−2.38 to +2.97** and predictions range from **2.95 to 6.81**. This is a small average fit change, not a validated improvement in individual safety decisions. Across 30 repeated splits with the chosen algorithm held fixed, V1 median MAE was 0.489 and V2 median was 0.475; these are not independent holdouts.

### Errors across the original seven-point scale

Diagnostic segments use the questionnaire's anchors: mean **below 4** is below neutral, **4 to below 5** is neutral to below agreement, and **5 or above** is agreement with intrusive descriptions. These segments summarize errors; they are **not** training labels or the marketer app's low/moderate/high classes.

| Observed response segment | Holdout n | V1 MAE | V2 MAE | V2 mean error (prediction − response) |
| --- | ---: | ---: | ---: | ---: |
| Below neutral, <4 | 10 | 1.333 | 1.315 | +1.315 |
| Neutral to <5 | 31 | 0.551 | 0.506 | +0.239 |
| Agreement, ≥5 | 126 | 0.449 | 0.445 | −0.346 |

Only **10** held-out respondents are below neutral; their errors cannot support a reliable low-intrusion classification. V2 still overpredicts the low group and underpredicts the high group, a pattern consistent with regression toward the mean and inadequate prospective features. For respondents with observed intrusion ≥5, V2 predicts **below neutral (<4) in 3 of 126 cases**, unchanged from V1, and **below agreement (<5) in 25 of 126**, up from **18 of 126** for V1. The bootstrap interval for the V2 high-segment MAE gain over V1 is **−0.015 to 0.023**. Thus V2 did **not** improve false reassurance; its higher below-agreement count is a material reason to keep it experimental.

The output also reports age, gender-code, and daily-use subgroup counts, MAE, and mean error. For example, V2 held-out MAE is 0.519 for ages 19–29 (n=33), 0.534 for ages 30–44 (n=87), and 0.454 for ages 45+ (n=47). These small, non-random subgroup comparisons do not establish fairness or population validity. Bootstrap intervals in this phase quantify uncertainty in **average errors for this fitted model**, not calibrated individual prediction intervals.

## Secondary-data search and treatment feasibility

The existing local data still lack a record containing a specified personalization condition, direct intrusiveness rating, and engagement outcome for the same ad and person. UPAD has events but no direct intrusion label or defined Level 0–4 exposure. The `.sav` has direct general intrusion ratings but no stimuli or levels. [Criteo](https://huggingface.co/datasets/criteo/criteo-uplift) has only binary ad targeting versus control and no intrusion. The local Gen Z workbook has perceived personalization and privacy/purchase statements, not assigned levels or direct intrusion.

The [Gen Z publisher record](https://data.mendeley.com/datasets/czgx8b793m/1) confirms that its agreement items use **1 = strongly disagree to 5 = strongly agree**, resolving a V1 documentation gap. It still does not publish a verified mapping for the separate click/purchase response codes in the local workbook, nor a five-level experimental treatment. V1's exploratory correlations remain self-report associations.

| Additional public lead | Actual accessible evidence | 49-C decision |
| --- | --- | --- |
| [Yu et al., Zenodo visual-presentation experiments](https://zenodo.org/records/22938743) | Three downloaded, publisher-MD5-verified workbooks (281, 305, 253 rows) with `Data` and `Codebook` sheets. Conditions are photo format, regulatory focus, and one parasocial scenario. Outcomes include purchase intention and attitudes, but **no direct intrusion or personalization treatment field**. See `results/phase3_external_dataset_audit_v1.json`. | Exclude from intrusion and threshold training. Preserve as audited research candidates. |
| [AI-generated personalized ad imagery preprint](https://arxiv.org/abs/2609.12697) | Published design has 100 people, four products, **three** levels and image-level attitude, purchase-intention, and creepiness measures. The accessed paper links a preregistration; no downloadable respondent-level results were found in the accessed materials. | Strong design reference, but no usable local data and three levels cannot be renamed as 49-C's five. |
| [Three-level personalization/creepiness experiment](https://proceedings.emac-online.org/index.cfm?The+Impact+of+Personalization+and+Transparency+Inf=&abstractid=A2022-107586) | Conference abstract describes a 3×2 experiment; no respondent-level dataset or codebook was linked in the accessed source. | Literature lead only. |
| [Digital personalization creepiness studies](https://onlinelibrary.wiley.com/doi/full/10.1002/mar.70089) | Several scenario conditions and intrusion-related measures; article states that data are available from the corresponding author on reasonable request. | No public row-level data inspected; not integrated. |
| [Personalization, brand, click intention and intrusiveness](https://zenodo.org/records/7003741) | Zenodo record contains the paper PDF only, not its Study 1/2 respondent data. | Conceptual reference only. |

No dataset with **all five defined treatments, measured engagement and intrusion, consent context, and respondent linkage** was verified. Published three-level findings are useful hypotheses but cannot identify five-level causal effects. The five-level `threshold_engine.py` therefore continues to return `insufficient_evidence`; no artificial level labels, survey-to-UPAD joins, or marketer-app predictions were added.

## Reproduce and next step

Use a compatible Python environment with `requirements-research.txt`. On this workstation, the bundled Python runtime has NumPy, pandas, and openpyxl; set `PYTHONPATH` to this project's `.vendor` directory for pyreadstat 1.3.7. On a **fresh copy** of the project, run `python survey_phase_v2.py` to create `results/survey_phase_v2.json` and `models/unsolicited_intrusiveness_respondent_v2.npz`, then run `python external_dataset_audit_v1.py` for the three downloaded Zenodo workbooks. Both scripts refuse to overwrite their versioned outputs, so archive those outputs before any deliberate rerun in this workspace. Run `python -m unittest discover -p 'test_*.py'` for regression tests. V1 and app files are preserved byte-for-byte in the Phase 3 checkpoint. A direct V2 rerun recomputed the selected candidate, coefficients, and holdout MAE exactly.

The next evidence acquisition step is a downloadable **secondary** respondent-by-ad dataset with explicit treatment definitions and consent context, identical respondents evaluating multiple ad creatives across the intended levels (or a justified design that identifies effects), direct intrusion/comfort ratings, and linked engagement outcomes including non-actions. Until then, use V1/V2 only for aggregate research on contemporaneous survey responses. Neither model supports individual marketer decisions or a calibrated 0–10 creative score.
