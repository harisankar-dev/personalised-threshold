# 49-C secondary-survey phase v1

**Date:** 6 November 2026  
**Scope:** independent consumer-perception analysis and respondent-level experiment; marketer app and five-level threshold engine remain at version 0.1.0.

## Dataset inventory and selection

The pasted phase note points to `amlbt/try`, which does not exist. The available secondary files are in `amlbt/try these dataset`, the project root, and `secondary_data/`. No survey records were joined to 49-C users, ads, or Criteo.

| Local dataset | Verified contents | Decision |
| --- | --- | --- |
| Consumer perceptions towards unsolicited ads on social media `.sav` | 837 respondents, 27 fields, including six direct 1–7 intrusiveness items, six privacy items, four ad-benefit items, four ad-avoidance items, and demographics | **Selected** for an independent direct-intrusiveness respondent study |
| Gen Z personalized-ads `.xlsx` | 296 rows, 35 Turkish-language columns covering perceived personalization, usefulness, relevance, novelty, privacy concern, and purchase-related statements | **Selected for exploratory analysis**; no direct intrusion items and no verified response codebook |
| Vietnam privacy-practices `.csv` plus local `CODEBOOK.pdf` and `Questionnaire for data.pdf` | 467 rows, 32 fields; collection, unauthorized use, improper access, errors, online trust, purchase intention | Relevant privacy context, but **excluded from intrusion training**: no ad-specific intrusion outcome or personalization-level treatment |
| UPAD tables and local `README (1).pdf` | User/ad events, privacy codes, ad metadata; audited in the 0.1.0 phase | Existing 49-C source; **no direct intrusion label**, unreliable event-level impression denominator, no five observed levels |
| Criteo Uplift | Binary advertising treatment, anonymized features, visit and conversion outcomes | Preserved as an isolated uplift benchmark; no intrusiveness or five-level treatment. See `CRITEO_UPLIFT_REPORT.md` |
| UW Ad Perceptions images/opinions | Problematic-content opinion labels and screenshots | Existing creative-screen diagnostic only; labels do not equal perceived intrusion |
| Online Shoppers Purchasing Intention `.zip` / CSV | Ecommerce session purchasing data | Excluded: no ad-intrusion or personalization exposure measure |
| Customer privacy concern workbook copies in root | One 1,125-row, 31-column survey with `P`-coded fields, repeated in copied files | Excluded pending a matching question/code dictionary; not treated as intrusion data |

The `.sav` source matches Romano and Han's [published data descriptor](https://doi.org/10.3390/data7100138): US social-media users completed an online survey in December 2021 about unsolicited ads. The questionnaire items and seven-point agreement anchors are printed in its Table 3 and methods. The file itself has no embedded question labels; the mapping below is inferred from column order and confirmed by its six item means matching Table 4. The local `CODEBOOK.pdf` and `Questionnaire for data.pdf` belong to the **Vietnam** dataset and must not be used to interpret the `.sav` or Gen Z workbook.

## Variable map and data audit

| `.sav` fields | Published construct / use | Model role |
| --- | --- | --- |
| `I1`–`I6` (published as `INT1`–`INT6`) | Feeling that ads based on previous online activities are invasive, intrusive, interfering, disturbing, distracting, or forced | **Direct target**: arithmetic mean on the original 1–7 agreement scale |
| `PC1`–`PC6` | Privacy concern about personalized social-media ads, permission, misuse, unwanted material, and data safety | Predictor composite, measured at the same time as the target |
| `PAB1`–`PAB4` | Perceived benefits of social-media ads | Predictor composite |
| `AAB1`–`AAB4` | Ad avoidance attitudes/behaviour | Descriptive only; excluded from predictors because avoidance can be a response to perceived intrusion |
| `Age`, `Gender`, `Frequency` | Age, gender code, social-media use frequency | Predictor demographics; no unique respondent identifier exists |
| `ITV_mean`, `PC_mean`, `PAB_mean`, `AAB_mean` | Source-supplied item means | Cross-check only; `ITV_mean` is never a predictor |

The `.sav` has **837 rows, no missing values in the modelled items, and two exact duplicate answer rows**. Both duplicates were retained because they may be different respondents with identical answers. The split keeps identical full response vectors in one partition. All six `I` item means reproduce the descriptor's Table 4 values, and `ITV_mean` exactly equals their row mean. The intrusiveness construct has Cronbach's alpha **0.906**, matching the published reliability. The raw-file age mean is **38.79**, while the descriptor reports **37.79**; this source discrepancy does not affect the model but should be acknowledged if age summaries are published.

The Gen Z workbook has **296 rows, 35 columns, zero missing cells, and one exact duplicate row**. Its birth-year entries span 1997–2012. No local source document establishes sampling, survey date, scale anchors, or the meanings of the separate 1–4 ad-click and 1–2 purchase response codes. Those codes are counted in the result file but are **not** interpreted as click or purchase rates. The last five questions mix purchase intention, self-reported purchase, and shopping frequency; their mean is called *purchase reaction*, not observed sales. The workbook does not measure direct intrusiveness.

## Exploratory associations

In the `.sav`, mean privacy concern and mean intrusiveness have Spearman rho **0.793**. This is an association between contemporaneous survey responses, and several privacy questions share discomfort/invasion wording with the intrusion questions. Ad avoidance is similarly associated with intrusion (rho **0.673**) but was excluded from the predictive feature set.

For Gen Z, the script groups the 1–5 item responses by **zero-based column positions**: personalization 7–11, usefulness 12–16, relevance 17–21, novelty 22–25, privacy concern 26–29, and purchase reaction 30–34. These groupings follow the item wording; their psychometric validity and response anchors are unverified. Spearman correlations with purchase reaction are:

| Construct | rho | 95% row-bootstrap interval (1,000 resamples) |
| --- | ---: | ---: |
| Perceived personalization | 0.673 | 0.594 to 0.745 |
| Perceived relevance | 0.697 | 0.630 to 0.759 |
| Privacy concern | 0.115 | −0.009 to 0.233 |

These data are cross-sectional self-reports. The first two associations support further research on relevance and perceived value; they do not establish that more personalization causes purchases. The privacy association is small and its interval includes zero. No Gen Z predictive model was deployed because the target is a mixture of response types and the response codebook and provenance are absent.

## Independent intrusiveness model

The **predeclared** target is the mean of six direct 1–7 intrusiveness items for each respondent. Two identical answer vectors were grouped in a seeded 80/20 holdout: **670 training respondents and 167 held-out respondents**. There is no respondent ID to check repeated people. Features were standardized using training rows only. The independent model is an L2 ridge regression (penalty 10, unpenalized intercept), clipped to the original 1–7 response range. Baseline predictions use the training target mean. The primary model uses age, gender, frequency, perceived ad-benefit mean, and privacy-concern mean. Ablations show what each block contributes; no holdout-tuned model selection was performed.

| Held-out model | MAE ↓ | RMSE ↓ | R² vs held-out mean |
| --- | ---: | ---: | ---: |
| Training-mean baseline | 0.815 | 1.028 | −0.066 |
| Demographics | 0.796 | 1.025 | −0.059 |
| Demographics + benefits | 0.796 | 1.022 | −0.052 |
| Demographics + privacy | 0.520 | 0.762 | 0.415 |
| **Predeclared combined model** | **0.521** | **0.764** | **0.411** |

The primary model's MAE improvement over the baseline is **0.294 points** on the seven-point scale, with a **0.195 to 0.385** row-bootstrap 95% interval (1,000 held-out resamples, fitted model fixed). Prediction-minus-observed mean error is **−0.135**: the model underpredicts on average. In the lowest prediction quintile it predicts 4.16 versus an observed 4.61; in the highest, 6.31 versus 6.60. Thus the model shows meaningful association in this dataset but is **not well calibrated at the extremes**. The privacy-only ablation is slightly better than the combined model on this one holdout; that difference is not a basis for switching models without a separate selection procedure.

### Interpretation boundary

This model predicts a person's **general survey agreement** about ads based on past online activity from their simultaneous privacy and benefit answers. It does not score an individual ad, an image, or a marketer's proposed targeting. It has no observed Level 0–4 exposures and cannot establish a personal threshold. The privacy and intrusion items share wording and response method, so held-out accuracy within this questionnaire is not external validation. Neither these predictions nor the Gen Z correlations are placed in the marketer app. `threshold_engine.py` continues to return `insufficient_evidence` for the available 49-C data.

## Files, reproduction, and next development step

The source `.sav` and `.xlsx` files were read only. `survey_phase_v1.py` writes `results/survey_phase_v1.json` and `models/unsolicited_intrusiveness_respondent_v1.npz` once, refusing to overwrite them. The previous baseline snapshot in `baselines/unversioned-2026-11-06/` and all earlier model artifacts remain in place. This folder is not a Git repository, so no Git checkpoint was possible. NumPy, pandas, openpyxl, and pyreadstat are required; this workspace has pyreadstat 1.3.7 in `.vendor`. Run `python survey_phase_v1.py` in a fresh copy of the project or archive the versioned outputs before deliberate reruns. Run `python -m unittest discover -p 'test_*.py'` for regression checks.

The next dataset search should prioritize **secondary ad-level studies with the same participants rating multiple actual creatives** and recorded personalization conditions, consent context, and direct intrusion/comfort responses. Such a dataset would permit a user-disjoint, ad-disjoint, calibrated evaluation of content and privacy effects. It must also observe valid engagement outcomes across Levels 0–4 before the five-level recommendation engine can move beyond `insufficient_evidence`.
