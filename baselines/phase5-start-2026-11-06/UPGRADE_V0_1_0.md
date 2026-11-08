# 49C evidence and release plan — first formal release 0.1.0

**Date:** 6 November 2026. **Data collection:** secondary sources only. This document interprets the supplied upgrade note under the user's earlier instruction not to conduct a primary survey. No market-size or legal figure from that note is used here without source verification.

## 1. Existing model assessment

The repository had no version tag or `VERSION` file before this upgrade. The pre-upgrade state is preserved in `baselines/unversioned-2026-11-06/` with SHA-256 checksums. It contains the current-at-snapshot source and output metrics, including the pressure-cue addition. The earlier privacy-only source was not preserved, so it cannot be reproduced as a separate code version. The raw CSVs and large cleaned event file remain in place; the snapshot records the analysis code and key result JSON files rather than duplicating those data.

`analysis.py` reads the supplied CSVs with their second line as headers, validates IDs and joins, excludes unknown-user events, and fits a user-grouped, regularized logistic regression. The observed target is **click versus like/share/comment among recorded action events**. Its ROC-AUC is 0.4993 on the grouped holdout, against 0.5000 for a constant baseline. This is not click-through prediction because no valid non-action impression denominator exists.

`intrusive_ad_model.py` is a hand-weighted creative screen. It OCRs image text and looks for privacy and pressure cues. Its low/moderate/high tiers and 0–10 number are **rubric outputs**, with no estimated accuracy or calibration against consumer intrusion ratings. The supplied image exposed how narrow the first privacy-only rubric was; adding pressure phrases fixed that case but did not establish generalization. The screen is an adjunct to the personalization-threshold study, not a substitute for a measured threshold model.

## 2. Gap analysis and data feasibility

| Requirement | Present evidence | Priority / risk | Release decision |
| --- | --- | --- | --- |
| Valid user/ad event join | 249,831 of 300,000 events join to known users and ads | High / addressed | Preserve cleaned events and exclusions |
| Non-click impressions | Not linked to individual user/ad events | High / target invalid | Keep engagement as click versus other **action** only |
| Five observed personalization treatments | Not present; age/country targeting dominates ad metadata | High / unidentified | Levels 0–4 remain a design contract |
| Behavioural relevance | Browsing is URL-like; purchase field includes device models | Medium / weak semantics | Do not report a validated TF-IDF relevance score |
| Privacy sensitivity | Permission code direction unspecified; setting codes name departments | High / wrong interpretation | Do not invent a composite privacy score |
| Direct perceived intrusiveness labels | Absent from original files and attached survey draft | High / model B unavailable | Abstain from intrusion prediction |
| Consumer-level threshold | No valid per-level engagement or intrusion response | High / counterfactual gap | `threshold_engine.py` returns insufficient evidence on current data |
| Creative screen | Privacy/pressure cue rubric and OCR | Medium / weak generalization | Retain as unvalidated adjunct, with visible evidence limits |
| External ad opinions | UW dataset: 500 screenshots with participant labels for clickbait, manipulation, design, etc. | Medium / label mismatch | Research benchmark only; do not relabel as personalization intrusion |

The fixed external diagnostic sampled 30 high-opinion-concern and 30 low-opinion-concern images (seed 49). Before the abstention change, 29/30 high-concern and 30/30 low-concern images were called low by the creative rubric. After the change, those 59 zero-cue images return `needs_review`; the remaining high-concern image remains high. This does **not** measure intrusiveness accuracy or show that the screen distinguishes the two opinion groups. It shows why a zero-cue OCR result must not be presented as evidence of a low-risk image. The pre/post audit files are preserved in `results/`.

The external dataset is [Zeng, Kohno, and Roesner's Ad Perceptions Dataset](https://github.com/eric-zeng/chi-bad-ads-data), copied into `secondary_data/chi-bad-ads-data/` for local research. It has 500 ads and opinions from 1,025 annotators. Its labels can support a separate problematic-content study, but none is a direct measure of **how intrusive a personalization level feels to a consumer**. No model trained on these labels is presented as Model B.

## 3. Data dictionary and provenance

| Field / source | Observed meaning | Use and restriction |
| --- | --- | --- |
| `UserTable.User_ID` | User key; 50,000 unique | Join key |
| `Gender`, `Race_Ethnicity` | Demographic codes | Not used in current predictor; avoid unnecessary protected-attribute use |
| `Privacy-Related_Features.User_ID` | 50,000 unique keys | Many-to-one join from events |
| `Data_Sharing_Permissions` | Codes 2–6, direction undocumented | Nominal category only; not a sensitivity scale |
| `Privacy_Settings` | Codes 20–31 map to departments | Nominal category only; not privacy strength |
| `user_consent` | Yes/no code | Observed record; permission status, not comfort or intrusiveness |
| `UserBehaviorTable.User_ID` | 31,600 unique across 50,000 rows | Not joined directly: 13,183 users have multiple rows |
| `Browsing_History`, `Purchase_History` | URL-like and device-model strings | Not validated product-interest or purchase features |
| `AdCharacteristicsTable.Ad_ID` | 60 unique ads | Join key and categorical baseline predictor |
| `Ad_Content` | Ad wording | Creative screen input; not treatment intensity |
| `Ad_Targeting_Criteria` | Mostly broad age/country descriptions | No per-user personalization treatment |
| `User_Interaction_Table.ID` | 300,000 unique event IDs | Preserved as `Event_ID` |
| `interaction_Type` | 32 like, 33 share, 34 comment, 35 click | Recorded action type, not exposure or comfort |
| `interaction.Impressions` | Ad-level summary | Excluded from event model: counts do not reconcile with event table |
| `results/clean_events.csv` | 249,831 valid joined action rows | Derived secondary-data table |
| `results/excluded_events.csv` | 50,169 unknown-user rows | Preserved with exclusion reason |
| Creative score and tiers | Weighted rule output | Proxy engineering demo; not measured ground truth |

The five questionnaire workbooks are duplicate copies with no supplied item wording or user/ad join key. The draft personalized-ad survey contains hypothetical scenarios, not respondent ratings. Neither supplies a target label.

## 4. Five-level operational design

| Level | Permitted creative information in a future study | Data-use gate |
| --- | --- | --- |
| 0 Generic | Product and offer only | No individual data |
| 1 Contextual/demographic | Broad context or permitted segment | Segment data authorized for this purpose |
| 2 Behavioural | General interest inferred from permitted behaviour | Behavioural use explicitly eligible |
| 3 Historical | Prior transaction or product relation | Historical use explicitly eligible |
| 4 Combined | Multiple permitted signals, with no gratuitous surveillance language | Every included signal eligible; sensitive data separately restricted |

These levels are **definitions for future comparable ad variants**, not labels found in the 60-ad source table. Consent is a hard gate at every level. The current `user_consent` code alone does not identify which categories and purposes were authorized. The engine therefore cannot infer eligible levels from the supplied CSVs.

## 5. Secondary ground-truth acquisition plan

Search for an existing dataset with respondent-level or ad-level ratings of **perceived personalization intrusiveness**, the exact ad shown, treatment level or enough ad metadata to construct it, and respondent/stimulus identifiers. Record instrument wording, rating anchors, sampling, consent, license, linkage quality, and whether exposure was randomized. Keep source populations separate; do not join unrelated ad-opinion ratings to 49C user IDs. The UW dataset may be used to evaluate problematic-content detection, but its clickbait/manipulative labels cannot be silently converted into intrusiveness ground truth. A [Mendeley Data study of 837 respondents](https://data.mendeley.com/datasets/zcp5httw5c/1) does report perceived intrusiveness toward unsolicited social-media ads; its published description does not establish linked ad stimuli or five personalization treatments, so it is a candidate for further inspection, not yet a trainable Model B source. If no matching secondary dataset is found, Model B and threshold efficacy stay pending.

## 6. Modelling and validation specification

**Model A, engagement:** first require valid impression-level positives and negatives with exposure time and a legitimate prediction point. Use prevalence-only and logistic baselines; group by user, fit encoding inside training folds, and hold out ads as a transfer check. Report ROC-AUC, PR-AUC, Brier/calibration, confusion matrix, class balance, and segment results. The existing action-type model remains a negative feasibility baseline and must not be renamed CTR.

**Model B, intrusiveness:** require directly measured ordered ratings. Retain the raw scale; compare an intercept/ordinal baseline with a justified ordinal or regression model. Split by respondent and separately by unseen ad/stimulus; report MAE, ordinal confusion matrix, per-class performance where tiers are used, calibration and uncertainty. A synthetic cue rubric cannot serve as training truth.

**Model C, threshold:** require both validated per-level outcomes in a comparable population. Use `threshold_engine.py` with explicit eligibility, an upper-bound intrusion ceiling, and lower-bound engagement choice. Compare with always-generic, maximum-eligible, and simple-rule policies only on valid held-out treatment data. Do not report policy uplift from the present observational files.

## 7. Decision contract and dashboard specification

`threshold_engine.py` accepts five possible levels, explicit eligible levels, a purpose-specific `consent_verified` flag, a risk ceiling, validated per-level estimates with intervals, and four evidence flags. Without verified consent, it restricts consideration to generic Level 0 even if higher levels were supplied. If any evidence flag is missing, it returns `insufficient_evidence` and no recommended level. Among allowed levels whose **upper intrusion bound** passes the ceiling, it selects the highest **lower engagement bound**, breaking ties toward less personalization. It never infers legal eligibility from a numerical risk score. Current 49C data fail the evidence gate.

The current local web app shows creative-screen results and the threshold status. A future business dashboard may show the source audit, action-type baseline, data-quality exclusions, and creative-screen examples as **observed**, **derived**, or **rubric** panels. Engagement-by-level, intrusion-by-level, frontier, and policy comparisons must remain visibly **unavailable** until valid secondary labels and per-level outcomes exist. Scenario sliders can be added only with a prominent **hypothetical illustration** label.

## 8. Risk and dependency register

| Risk | Current control | Dependency to resolve |
| --- | --- | --- |
| Overfit creative rules | Show cue evidence; do not claim accuracy; preserve failure cases | Independent labelled ads matching the target construct |
| OCR misses visual content | Mark image objects/layout unassessed; no reassuring validation claim | Validated vision pipeline and image holdout |
| Clicks confused with comfort | Separate action-type analysis from intrusion model | Direct perceptual ratings |
| Aggregate/event mismatch | Exclude ad-level impression summary | Reconciled exposure records |
| Consent overreach | Require externally supplied eligible levels; default current status abstains | Purpose-specific permissions and legal review |
| Demographic or source shift | No deployment claim; require segment and unseen-ad checks | Broader secondary data with adequate labels |
| External dataset label mismatch | UW data quarantined as research evidence | Direct personalization-intrusion label source |

## 9. Version map and reproducibility

- **Unversioned snapshot:** `baselines/unversioned-2026-11-06/` with code, key outputs, and `sha256.json`. It records the then-current pressure-cue screen, not the lost privacy-only source.
- **0.1.0:** `threshold_engine.py` adds evidence-gated, consent-constrained decision logic; `intrusive_ad_model.py` and the local UI report threshold unavailability; `VERSION`, `requirements.txt`, `package.json`, tests, and this document make the state explicit. No new intrusiveness predictor was trained.
- **Migration:** existing `classify()` tier/score fields remain; `predict()` adds `model_version` and `threshold_decision`. The server must be restarted after code updates. Future data/model versions must be named separately.
- **Run:** use Python 3.12 with `requirements.txt`, Node.js with `package.json` for OCR, `python analysis.py`, `python screen_dataset.py`, and `python -m unittest discover -p 'test_*.py'`. Source CSVs are read only. `analysis.py` regenerates `results/` outputs, so preserve a copy of any result you need to compare before rerunning.

The original academic question remains pending because the required per-level and perceptual outcomes are absent. The current release provides a reproducible feasibility study, a narrow creative-risk screen, and an executable decision contract that abstains on unsupported recommendations.
