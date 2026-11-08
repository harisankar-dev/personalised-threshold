# Phase 5 — model consolidation and reliability validation

**49-C: The Personalization Threshold | 7 November 2026 | Secondary data only**

## Executive finding

The project is a reproducible **feasibility study and marketer creative-screen prototype**, not a validated model of an individual's personalization threshold. Some separate respondent-level surveys support prediction of **general-ad intrusion questionnaire ratings**, with material extreme-response and transfer limitations. Criteo supports an isolated binary-treatment visit benchmark. The marketer app's 0–10 score and three tiers are an explicit **rule rubric** for visible creative cues, not a calibrated probability or measured consumer reaction. No available source jointly measures five assigned personalization levels, direct intrusion responses, ad content, consent context, and engagement for the same exposure. `threshold_engine.py` correctly returns `insufficient_evidence`.

Three user-supplied ZIP datasets were also audited during this phase. Every extracted file is an exact copy of an existing local dataset. See `THREE_DATASETS_EVALUATION_REPORT.md` for source links, column mapping, quality checks, use decisions, and the new separate Vietnam privacy/trust descriptive analysis.

## Scope and preservation

The pre-change folder had **no Git repository**, so `git status` could not establish a diff. Before any edit, `baselines/phase5-start-2026-11-06/` preserved 61 key code, document, model, and small-result files, plus a SHA-256 manifest of 81 paths including source hashes. Before touching supplied ZIPs, `baselines/three-user-zips-start-2026-11-07/` preserved 63 in-progress files and the three original ZIP hashes. All pre-existing research models, V1/V2/V3, Criteo artifacts, Phase 4 results, original datasets, and threshold behavior remain in place. The only pre-existing app file edit is one factual explanatory sentence in `web/index.html`; no scoring code was retuned.

This phase inspected the original `analysis.py` outputs, V1/V2 and Phase 4 reports, all saved result/model artifacts, Criteo analyses, creative-screen diagnostic, marketer app, threshold engine, regression tests, and source data/codebooks. `phase5_repro_audit.py` replays saved experiments in a temporary directory and compares output structures and model arrays without overwriting the reference artifacts.

## Evidence matrix and readiness

| Component | Unit and outcome | Evidence and fair comparator | Validated scope | Readiness |
| --- | --- | --- | --- | --- |
| Original UPAD event model | Recorded user–ad **action**: click versus like/share/comment, not exposure-level CTR | 49,940 user-disjoint holdout actions; logistic AUC **0.4993**, Brier **0.18824**, versus constant AUC 0.5000, Brier **0.18820** | Audit and negative feasibility result; no useful predictive gain | **Research audit only** |
| Creative screen (`intrusive_ad_model.py`) | Uploaded text/image; visible pressure/privacy cues; rubric score 0–10 and low/moderate/high or `needs_review` | Deterministic sanity cases; one aggressive supplied screenshot scored high 10/10 in live browser. UW image diagnostic found 29/30 high-opinion-concern images required review after zero-cue abstention | Explainable creative **screening**, no calibrated intrusion accuracy or generalized visual understanding | **Working prototype, unvalidated predictor** |
| Survey V1 (Romano–Han) | 837 survey respondents; mean of six direct general-ad intrusion items, range 1–7 | 167-person held-out MAE **0.521** versus training-mean **0.815** | Same-survey association with contemporaneous privacy answers | **Experimental** |
| Survey V2 (same source/holdout) | Same respondent target | MAE **0.509** versus V1 **0.521**; paired gain 95% CI **[-0.0033, 0.0282]**, includes zero | Training-only selection; no reliable incremental improvement or external validation | **Experimental; do not promote** |
| Survey V3 uncertainty (same source) | Prediction intervals for general-ad survey rating | On **reused** 167-person holdout, nominal 90% two-sided coverage **149/167 = 89.2%**; below-neutral coverage **5/10 = 50%** | Marginal interval audit only; exchangeability and subgroup coverage unresolved | **Experimental** |
| Independent Redondo/Aznar web-ad survey | 1,511 different respondents; general web-ad intrusion on **−3 to +3** | 302-person holdout MAE **0.840** versus training-mean **0.955**; bootstrap gain CI **[0.066, 0.165]** | Separate within-source benchmark; incompatible target wording, scale, feature set and ad context with Romano–Han | **Experimental, separate external-source benchmark** |
| Criteo visit prediction/uplift | Binary ad-treatment records; visit/conversion, **no intrusion** | Exact-feature-vector-disjoint 39,983-row holdout. Control AUC **0.9448**, Brier **0.02669** versus constant **0.03717**; treatment AUC **0.9259**, Brier **0.03309** versus constant **0.04603**. Uplift AUUC gain **0.00158**, bootstrap CI **[-0.00063, 0.00378]** | Stronger visit prediction; uncertain ranking lift, no five-level threshold | **Experimental benchmark only** |
| Gen Z perceived personalized ads | 296 self-report records; perceived tailoring, relevance, privacy, behavior codes | Existing descriptive V1 audit; exact duplicate in supplied ZIP | Associations only; no direct intrusion or assigned personalization | **Descriptive only** |
| Vietnam privacy/trust | 467 selected online-market respondents; privacy, online trust, stated purchase intention | New scale and Spearman audit; no supervised target suitable for 49-C | Privacy/trust context only, no ad intrusion | **Descriptive only** |
| Five-level threshold engine | Per-person recommended personalization level subject to consent and intrusion bound | Required joint data absent; contract tests enforce abstention | No valid recommendation from current datasets | **Unsupported; `insufficient_evidence`** |

These metrics are **not interchangeable**. In particular, a −3..3 general web-ad intrusion score cannot be compared numerically with a 1..7 unsolicited-social-ad score, and neither measures the response to an uploaded marketer creative. Privacy concern is related to, but not identical to, intrusion. Criteo's binary treatment estimates a different question entirely. An exact duplicate ZIP does not count as cross-dataset validation.

## Reliability findings

### High-intrusion false reassurance and low-response failure

Of the Romano–Han V1/V2 holdout's **126 observed high-intrusion** respondents (mean rating ≥5), V1 predicted below 5 for **18**, while V2 did so for **25**. Both predicted below neutral 4 for **3**, including **one** severe-high case (mean ≥6). V2's smaller overall MAE therefore came with worse high-case reassurance at the agreement boundary. This was **not** grounds to deploy V2. Its high-case comparison is on a holdout already inspected during model development.

V3's split-calibrated two-sided interval has median width **2.342** points on a seven-point scale. Overall 149/167 observations fell within it, but only **5 of 10** below-neutral responses did; the small subgroup makes that estimate imprecise. Its one-sided upper bound covered only **143/167 = 85.6%** of observations, and **6 of 126** high-intrusion ratings had an upper bound below 5. A nominal marginal guarantee does not provide acceptable per-segment reassurance. These calibration estimates use the repeatedly examined outer holdout and require exchangeability for future validity; neither condition warrants a deployment guarantee.

The independent Redondo/Aznar benchmark improved average error but predicted its **26 negative-intrusion** held-out respondents with MAE **2.528** and positive bias **2.528**; the 233 positive-intrusion respondents had MAE **0.634**. Average performance conceals that important low-tail failure. Its data and target were kept separate from Romano–Han.

V2's saved age segments report MAE **0.519** for ages 19–29 (n=33), **0.534** for 30–44 (n=87), and **0.454** for 45+ (n=47); daily social-media users have MAE **0.555** (n=125) versus **0.370** for less-than-daily users (n=42). These descriptive gaps warrant caution; small groups and repeated holdout examination preclude stable fairness claims. No protected-class safety certification is claimed.

### Overfitting, leakage, and measurement compatibility

The original action model groups its holdout by user. The Criteo v3 split groups exact 12-feature vectors because no user ID is supplied; this prevents duplicate feature profiles crossing train/test but **cannot** establish person-level independence. Criteo's uplift confidence interval spans zero. V1/V2 use a fixed respondent-level holdout, regularization, training-only feature selection and cross-validation, but the same holdout has been examined in successive phases. Further tuning against it would overfit research decisions. V3 uses separate calibration rows but reports on that reused outer holdout.

The Romano–Han privacy and intrusion item averages correlate **0.760** in the saved audit. Both are asked in the same survey, creating plausible construct overlap, response-style, and contemporaneous-information leakage for practical use. A marketer uploading only ad text/image cannot supply those respondent answers. The 1,511-person independent survey proves that another source can support a separate general-intrusion benchmark; it does **not** externally validate V1/V2 coefficients because the target scale, question wording, sampling, and predictors differ. No cross-source record joins were made.

The creative screen's OCR and visible-cue rules require separate evidence from human ratings on actual uploaded creatives before 0–10 could be interpreted as perceived intrusion. In the archived 60-image UW diagnostic, 29/30 high-opinion-concern images generated zero matched cues before abstention; after abstention these require review, avoiding a false *low* output on those cases. The other 30 low-opinion-concern images also required review, so this diagnostic demonstrates a coverage limitation, **not** discriminative validation. The aggressive supplied screenshot is a useful regression example, not a generalization estimate.

### Source compatibility for an actual threshold

A defensible five-level recommendation would need, for the same exposure/respondent, a verified treatment or otherwise identifiable exposure level, direct perceived intrusion, consent/context, and engagement; it would also need sufficient support at each level, independence and held-out validation, calibrated uncertainty, and high-risk false-reassurance checks. Current sources split these constructs across unrelated people, different questionnaires, and incompatible scales. No fabricated levels or proxy intrusion labels were created. `threshold_engine.py` continues to abstain.

## Reproducibility and application check

`phase5_repro_audit.py` replays seven saved research outputs in temporary locations: original UPAD audit/baseline/associations, Romano–Han V1 (including Gen Z descriptive audit), V2, V3 uncertainty, Redondo/Aznar, Criteo v3 visit modelling, and Criteo uplift bootstrap validation. It verifies source hashes, result values, and saved model arrays to strict numerical tolerance, and audits the checkpoint manifest for unexpected edits. The final machine-readable result is `results/phase5_repro_audit.json`. Exact original experiments are preserved; replay is a **reproducibility check on the same data**, not new external validation.

The marketer app was run locally and exercised in a **real browser** on 7 November 2026. A generic text ad produced low 0/10; a privacy-and-pressure text case produced high 9/10; the supplied aggressive PNG produced high 10/10 with OCR-extracted countdown/scarcity/discount and repeated-exclamation cues. Its displayed threshold status said evidence cannot support a consumer-level personalization threshold. Reset worked and no runtime error appeared. A misleading sentence in `web/index.html` was corrected to: “Available surveys rate ads in general; none rates the creatives uploaded here.” This is a smoke test of the app, not a human-rated accuracy study.

For this Windows workspace, use the project-pinned `requirements-research.txt` dependencies (numpy, pandas, openpyxl, pyreadstat). The exact final validation command from the project root was:

```powershell
$env:PYTHONPATH=(Resolve-Path .vendor).Path
& 'C:\Users\imhar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -q
```

`phase5_repro_audit.py` was run with that same interpreter and `PYTHONPATH`. Saved versioned scripts intentionally refuse silent overwrites. For a fresh replay, use a **copy** of the project in a new directory, or direct outputs to a new versioned destination. Do not regenerate outputs over the preserved baselines.

## Files changed and verification

**New Phase 5 files:** `baselines/phase5-start-2026-11-06/`, `baselines/phase5-repro-prototype/phase5_repro_audit.json` (preserved first replay), `phase5_repro_audit.py`, `test_phase5_repro_audit.py`, `results/phase5_repro_audit.json`, and this report. **Three-ZIP work:** all files listed in `THREE_DATASETS_EVALUATION_REPORT.md`, including a second checkpoint and separate Vietnam analysis. **Existing files edited:** `web/index.html` (one explanatory sentence), `PROJECT_STATUS.md`, `CHANGELOG.md`. No existing model, dataset, experiment output, scoring logic, or threshold logic was modified.

**Final verification:** 41 of 41 regression tests passed (the Phase 4 baseline was 35; this phase added six focused tests). The exact experiment replay passed for all **seven** research outputs, and the Vietnam descriptive analysis reproduced an exact JSON match in a temporary output. The checkpoint audit found **78 of 81** checkpointed paths unchanged; the other three are the intentional `CHANGELOG.md`, `PROJECT_STATUS.md`, and `web/index.html` edits. All 20 checkpointed source-data hashes match. The initial full-test attempt exposed two Windows temporary-directory cleanup errors in the new ZIP-path tests; those tests were corrected to use a non-created workspace path, and the complete suite was rerun successfully. No model metric changed during that fix.

## Final component status and limitations

The local app is **operational as an explainable screening prototype**. Its score is a rubric score, and an uploaded image without recognizable cues can still be uncertain or require review. Respondent-level intrusion models are **research experiments** with weak extreme-case reliability and no ad-creative bridge. Criteo is a **separate engagement benchmark**. Vietnam/Gen Z are **descriptive context**. The five-level personalization threshold is **unsupported and abstaining**. The remaining research gap is a compatible, public secondary dataset that observes five well-defined personalization exposures with direct intrusion responses and engagement on the same unit; none of the supplied sources closes it.
