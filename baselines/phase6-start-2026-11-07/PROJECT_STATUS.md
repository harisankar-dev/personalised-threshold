# 49C project status — secondary data only

## Phase 5 and three supplied ZIP datasets — 7 November 2026

Phase 5 consolidated the existing evidence, replayed the saved experiments without replacing artifacts, tested the marketer app in a real browser, and documented high-intrusion false reassurance, low-tail errors, calibration, subgroup differences, and cross-dataset incompatibility. See `PHASE5_MODEL_VALIDATION_REPORT.md` and `results/phase5_repro_audit.json`. The app is an operational **creative-screen prototype**; its 0–10 value is a rule-rubric score, not a calibrated consumer perception. The five-level threshold remains `insufficient_evidence`.

Three newly supplied ZIPs were safely extracted and audited. All five extracted files are byte-identical to existing local secondary sources, so they add no independent validation respondents. The Vietnam privacy-practices survey now has a separate, checksum-verified descriptive scale/association analysis; the Gen Z workbook and Romano–Han source retain their existing separate uses. See `THREE_DATASETS_EVALUATION_REPORT.md` and `results/vietnam_privacy_trust_v1.json`. No primary survey or cross-dataset respondent join was performed.

## Current result

The folder now contains a cleaned, reproducible secondary-data analysis, a three-tier ad screening prototype, and a revised [second-review manuscript](49C_V2_DRAFT.md). The user has ruled out a primary survey. The original 49-C ad/event files have no personalization-level treatment or perceived-intrusiveness label, so the original consumer-specific threshold cannot be estimated from them. A separate secondary survey now supplies direct **general respondent-level** intrusion ratings, but no linked ad creative or five-level treatment. The prototype returns rubric-defined content-risk tiers for new text or image ads; the report does not call them measured consumer perceptions.

Release `0.1.0` is documented in `UPGRADE_V0_1_0.md` and `CHANGELOG.md`. A snapshot of the previously unversioned code and key outputs is in `baselines/unversioned-2026-11-06/`. `threshold_engine.py` implements consent and risk constraints but abstains on the present data. The locally downloaded UW ad-opinion dataset is kept as an external research source; its labels do not measure this project's personalization-intrusion outcome.

The linked Criteo Uplift dataset has now been audited and evaluated separately. Its binary advertising treatment supports a visit-uplift benchmark but has no direct intrusion label, ad creative, or five-level personalization treatment. The held-out visit predictor beats a constant baseline, while uncertainty around uplift ranking includes zero. See `CRITEO_UPLIFT_REPORT.md`. No Criteo values appear in the marketer app or threshold recommendation.

The next secondary-survey phase found six direct intrusion items in the 837-person unsolicited-social-ads SPSS file. An isolated respondent-level ridge model improved held-out MAE from 0.815 (training-mean baseline) to 0.521, largely through simultaneously reported privacy concern; calibration at response extremes and external validity remain weak. The 296-row Gen Z workbook supports descriptive associations but no validated intrusion target. See `SECONDARY_SURVEY_PHASE_V1.md`. These results do not enter the marketer app or alter the five-level evidence gate.

Phase 3 reproduced V1 exactly and tested its validity limits in `SURVEY_PHASE_V2_REPORT.md`. Privacy and intrusion answers have substantial wording and response overlap. Training-only selection yielded an experimental V2 with held-out MAE 0.509 versus V1's 0.521, but the paired improvement interval crosses zero. Among 126 high-intrusion respondents, V2 predicted below the agreement boundary for 25, compared with 18 for V1. Only 10 held-out respondents rated intrusion below neutral. V2 remains separate from the app. Three additional public experiment workbooks were audited and excluded because they lack direct intrusion and personalization-level treatment. The five-level threshold remains `insufficient_evidence`; no primary survey is planned.

Phase 4 added a training-only calibrated uncertainty audit and a fully separate 1,511-person public web-ad-intrusion survey benchmark. The uncertainty audit's reused-holdout two-sided interval covered 149/167 respondents but only 5/10 below-neutral respondents; its one-sided upper bound missed six high-intrusion respondents at the agreement boundary. The independent survey model improved average held-out MAE to 0.840 from a 0.955 training-mean baseline, yet had MAE 2.528 for the 26 negative-intrusion respondents. See `PHASE4_SECONDARY_DATA_REPORT.md`. Both are research artifacts; the app and threshold engine are unchanged.

The external creative diagnostic showed 29 of 30 sampled high-opinion-concern images received a low score from the OCR rule screen before abstention. Zero-cue images now return `needs_review`. This avoids a false low-risk conclusion but is not a trained general-purpose image model or a validated intrusiveness predictor.

The supplied ADHERE paper addresses disruptive ad placement under Better Ads Standards. The report compares that task with 49C's content screening. After an aggressive image ad exposed a failure, the prototype added pressure-tactic cues alongside its privacy cues. The original privacy-only screen returned low, 0/10 on that image; the revised screen returns high, 10/10. The two cue totals remain separate in the result, and the prototype borrows ADHERE's explain-and-suggest-repair workflow.

## Completed work

| Review feedback | Completed response |
| --- | --- |
| Resolve IDs and publish exact join counts and missingness | `analysis.py` writes `results/audit.json`, 249,831 valid event joins and 50,169 excluded unknown-user events; all core table column missingness is listed. |
| Document the analytic unit | One recorded user–ad action event. The clean file does not represent impressions or non-actions. |
| Resolve repeated behavior IDs | 50,000 rows represent 31,600 users; 13,183 IDs repeat. Behavior is excluded from direct event joins to prevent multiplication. |
| Implement supported baselines | Constant click share and regularized logistic regression on ad and privacy codes, evaluated on disjoint users. ROC-AUC 0.5000 versus 0.4993. |
| Define an intrusiveness outcome | No defensible intrusiveness measure exists in these secondary files. Consent is not a substitute. This limitation is stated explicitly. |
| Reconcile ad aggregates | Zero of 60 ads have matching action counts between aggregate and event tables; four summary rows have more clicks than impressions. Aggregate metrics are excluded from the event model. |
| Conclusion, reproduction, AI declaration | Included in `49C_V2_DRAFT.md`; repository URL remains unavailable because no public repository was supplied. |

## Files to use

- `analysis.py`: data audit, cleaning, conditional-action baseline, and association analysis.
- `results/clean_events.csv`: 249,831 joined action rows with preserved event IDs and coded privacy fields.
- `results/excluded_events.csv`: 50,169 excluded events with `unknown_user` reason.
- `results/audit.json`: source sizes, missingness, duplicate keys, joins, and aggregate reconciliation.
- `results/associations.json`: conditional click fractions and Cramér's V by available code.
- `results/baseline.json`: grouped holdout metrics and precise model scope.
- `49C_V2_DRAFT.md`: secondary-data report draft for review and adaptation to the submission format.
- `intrusive_ad_model.py`: text or image input, OCR integration, explainable three-tier and 0–10 rubric scores, plus cue-linked editing suggestions.
- `marketer_app.py` and `web/`: local browser interface for marketer text or image input.
- `screen_dataset.py` and `results/ad_screen_results.csv`: apply the rule to all 60 supplied ads.
- `MODEL_README.md`: algorithm, usage, and limits.
- `SURVEY_PHASE_V2_REPORT.md`: Phase 3 measurement audit, V1/V2 comparisons, extreme-error checks, secondary-data search, and evidence limits.
- `PHASE4_SECONDARY_DATA_REPORT.md`: new secondary-source audit, independent web-ad-intrusion benchmark, uncertainty calibration, and five-level feasibility decision.
- `survey_sanity_cases.json` and `test_model.py`: six fictional ad conditions from the supplied survey used as reproducible checks, with no participant ratings claimed.

## Reproduce

Keep the supplied CSV files beside `analysis.py`, install Python with `pandas` and `numpy`, and run `python analysis.py`. The script does not alter source files. The user-grouped split uses seed 49. The output folder is regenerated on each run.

## Decision needed for final submission

The original project title promises an individual intrusiveness threshold, which these files cannot support. The revised title frames the work as a secondary-data feasibility study. The team should use that honest scope for submission or obtain another **secondary** dataset that directly measures both personalization exposure and intrusiveness. No additional primary data collection is part of this plan.
