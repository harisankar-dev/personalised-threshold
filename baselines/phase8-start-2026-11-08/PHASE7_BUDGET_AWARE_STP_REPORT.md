# Phase 7 — budget-aware STP strategy, survey profiles and pre-launch advisory

**49-C | 7 November 2026 | Secondary data only**  
**Product status:** Operational local pre-launch **advisory prototype**, not a validated audience-level optimization or five-level personalization-threshold model. No primary survey, ad publication, real campaign change, fabricated uplift, invented financial value or cross-dataset respondent join occurred.

## 1. Starting evidence and preservation

I reviewed `STP_DATA_MODEL_FEASIBILITY_AUDIT.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, Phase 1–6 reports, source/codebook audits, current survey/Criteo/UPAD result JSONs and NPZ artifacts, `threshold_engine.py`, marketer app, research dashboard, creative rubric and regression tests. The original 0–10 screen is an explicit text/OCR cue rubric, not a fitted perception model. UPAD's 49,940-row user-disjoint recorded-action holdout had logistic AUC **0.4993** versus constant **0.5000**; its table has no impression denominator or perceived-intrusion response. Criteo predicts within-arm visits in a binary treatment study, but the uplift-ranking gain interval **[−0.000626, 0.003784]** includes zero and it has no direct intrusion or five levels. Romano V1/V2 and independent Redondo survey models predict *general-ad questionnaire ratings* with marked extreme-response error and no uploaded-ad bridge. Gen Z and Vietnam analyses are descriptive. `threshold_engine.current_dataset_status()` returns `insufficient_evidence`.

This folder has **no Git repository**, so `git status` cannot represent the starting diff. Before edits, `baselines/phase7-start-2026-11-07/` copied **81** then-current code, document, small-result and NPZ files and recorded SHA-256 values for seven original secondary source files. This checkpoint is recoverable; no original data or model artifact was replaced. At final check, **74/81** checkpointed files matched, **seven** were the expected app/documentation edits, and **none** were missing. All seven selected source hashes, all checkpointed saved research JSONs and all checkpointed NPZ artifacts matched. The new Phase 7 result has its own filename. The old Phase 5/6 experiments and reports remain intact.

## 2. Dataset/variable mapping and actual segmentation analysis

Two independent secondary surveys support cautious *descriptive* preference profiles:

| Separate source | Verified items | Cutoff and interpretation | Actual profile sizes |
|---|---|---|---|
| [Gen Z personalized-ad survey](https://data.mendeley.com/datasets/czgx8b793m/1), 296 rows | Mean of original Turkish **relevance** columns 17–21 and **privacy concern** columns 26–29 (zero-based); publisher documents 1–5 agreement direction. | Higher axis average ≥**3.5**, lower <3.5. | Higher relevance/lower concern **33** (11.1%); higher/higher **88** (29.7%); lower/lower **82** (27.7%); lower relevance/higher concern **93** (31.4%). |
| [Romano–Han unsolicited-social-ad survey](https://data.mendeley.com/datasets/zcp5httw5c/1), 837 rows | Mean `PAB1–PAB4` **perceived ad benefits** and `PC1–PC6` **privacy concern** on a 1–7 general-ad scale. | Higher axis average ≥**4.5**, lower <4.5. | Higher benefits/lower concern **110** (13.1%); higher/higher **500** (59.7%); lower/lower **46** (5.5%); lower benefits/higher concern **181** (21.6%). |

`phase7_segmentation.py` validates source SHA-256, size, item order and response bounds, calculates item means and Cronbach alpha, applies a **predeclared midpoint-based two-axis rule**, then saves aggregate counts/shares and 2,000-resample within-source bootstrap intervals in `results/phase7_segmentation_v1.json`. Gen Z alpha is **0.8712** relevance / **0.8723** concern; Romano **0.9482** benefits / **0.9211** concern. Value–concern Spearman correlations are **0.1772** and **0.1599** respectively. These measure within-source association, not an individual's willingness to receive specific targeting.

**Stability:** Gen Z leave-one-item-out assignment agreement ranges **90.9–97.0%**; Romano **95.0–97.4%**. Moving both cutoffs ±0.25 changes Gen Z assignments to **88.5%** agreement in either direction; Romano agreement is **94.4%** at −0.25 and **88.2%** at +0.25. For example, Romano's higher-benefit/higher-concern cell changes from 500 to 436 at +0.25. Bootstrap intervals, exact counts and limitations are in `PHASE7_SEGMENTATION_EVIDENCE.md`. These are sensitivity/within-sample checks, **not** external or temporal segment validation. One Gen Z and two Romano complete response vectors repeat, with no respondent ID to establish duplicate people. Gen Z has 18 birth years from 2009 onward that conflict with the publisher's “adult” sample description in 2026. The surveys have different referents, no common identity, no assigned ad treatment, and no campaign audience bridge. No cluster algorithm was added because it would not solve those gaps. No segment is called “personalization comfortable,” given a conversion probability, or recommended for exclusion.

The Vietnam online-market survey remains a separate privacy/trust source, not a personalized-ad profile. UPAD permission `level1`–`level5` codes are not the project's personalization treatments; Criteo binary treatment cannot become five levels. No external data download was needed in this phase.

## 3. Ad-feature and STP evidence boundary

The existing creative screen still extracts marketer-entered English ad text and printed English text from uploaded images using local OCR. Its regexes detect selected visible surveillance/tracking references, direct identifiers, browsing/purchase mentions, location specificity, selected sensitive personal facts, consent wording, pressure, urgency, scarcity, extreme discount and alarmist claims. It cannot see image objects, category, visual placement, actual targeting data use or factual truth of an offer. It has **no sentiment or emotional-tone classifier**, no validated product/service-category extractor and no ad-specific consumer-perceived-intrusion outcome. Positive sentiment would not establish low intrusion; therefore no unsupported sentiment model was added. The 0–10 value remains capped rubric points, and image-with-zero-cues remains `needs_review`.

The Phase 7 form distinguishes (A) observable copy/OCR cues, (B) **marketer-declared** targeting method, permission and audience eligibility, and (C) direct consumer intrusion survey answers from *different*, unrelated records. The app does not equate these. The aggregate survey profiles appear in a collapsible, source-labelled panel with an explicit “not this campaign audience” warning. They do not drive individual targeting. No protected/sensitive demographic is used for exclusion. Declared sensitive targeting or unresolved consent/eligibility for demographic/behavioral/historical/combined methods triggers `hold_for_review`; this is a conservative review rule, not a legal determination.

## 4. Budget-aware optimization framework actually implemented

`stp_advisory.py` compares the five ordered options **A keep**, **B revise one existing creative**, **C adjust targeting in the same campaign**, **D test one additional variant**, **E consider multiple segment-specific variants**. It always displays A. Its current action may be `keep_current_campaign`, `revise_one_creative`, or `hold_for_review`; it **never** recommends C–E automatically without evidence of segment-level incremental response. A creative with moderate/high rubric cues can prompt a one-creative *editorial* revision, provided no permission blocker and no known budget shortfall. No cues or financial justification leaves A as the default. A privacy/eligibility blocker, unassessable image or unaffordable known revision holds for review. Suggestions to rewrite wording remain hypotheses until tested.

**Entered economic variables:** currency; total campaign budget; already committed spend; costs for revision, targeting change, each additional creative, segmentation and extra management; number of additional variants; contribution margin per conversion; optional existing CPC, CPM, conversion rate and audience reach; optional user-defined worst/central/best **extra conversions** for a selected option. **All are optional except when their calculation needs them.** Missing figures stay `Unknown`; invalid negative/nonfinite amounts and inconsistent committed spending cause an input error. No default CPC, CPM, conversion rate, margin, ROI, ROAS or uplift was inserted. CPC/CPM/conversion/reach provide context; without compatible causal response evidence they are not used to invent option performance.

The **total budget ceiling includes existing campaign commitments and every additional implementation expense**. Headroom = budget − committed spend. Option costs are B=`revision_cost`; C=`targeting_cost + management_cost`; D=`variant_cost + management_cost + segmentation_cost`; E=`variant_count × variant_cost + management_cost + segmentation_cost`. A costs zero. An option is affordable only if its full known cost ≤ known headroom. The option table keeps **budget and permission status in separate columns**; a budget-feasible option can still be held or unverified for targeting eligibility. No additional media spend or reduction in current media spend is assumed. If the campaign must reallocate media, this calculator does not estimate the performance loss and must not imply feasibility. Where a positive contribution margin is entered, break-even extra conversions = `ceil(additional cost / margin)`. Optional scenario net value = **user-entered extra conversions × user-entered contribution margin − additional implementation cost**. Scenario results are explicitly hypothetical and **cannot** authorize a rollout recommendation. When reach is missing or small, fragmentation remains a warning; reach alone is not proof of sufficient per-variant learning volume. The full formula and input contract are in `PHASE7_STP_DECISION_LOGIC.md`.

### Hypothetical software checks — not company results

| Fixture condition | Observed software outcome |
|---|---|
| No finance data, generic copy | Keep current campaign; headroom, other-option costs and break-even shown as unknown. |
| Budget 1,000, committed 900, revision 20, margin 12, moderate pressure copy | Advises one revision within 100 headroom; 2 extra conversions to break even. One-variant fixture cost 160 is over budget. |
| Variant cost 90 + management 20 + segmentation 40, margin 30; worst/central/best extra conversions 0/5/9 | Hypothetical net values **−150/0/+120**; action still keeps current campaign on generic copy, because uplift is not validated. |
| Tight 30 headroom; one-variant cost 40 and three-variant cost 90 | Both are over budget; no fragmentation recommendation. |
| Behavioral targeting without verified permission, historical without permission, combined without verified eligibility, or sensitive method | Hold for review, regardless of appealing scenario arithmetic. |
| Unassessable image or known revision cost over headroom | Hold for review. |
| Invalid/negative/nonfinite costs, overspent budget, invalid rate/count, reversed scenario order | Explicit input error. |

All numbers in this table are **test fixtures** only. They are not observed marketing costs, outcomes or model estimates.

## 5. Product integration and readiness

The existing `POST /api/analyze` behavior is backward compatible: without `campaign`, its prior creative response fields are unchanged; with `campaign`, it adds a separate `strategy` object. The new UI lets the marketer declare objective, method, permission and eligibility, enter budget/committed spend, expand optional cost/performance and what-if panels, and compare options and break-even figures. The creative result, cue explanations, editing suggestions and five-level abstention remain visible. The UI uses text assignment for user-entered content and source-separated aggregate profiles. No survey or Criteo model is invoked on uploaded creative. The research dashboard is unchanged and still reads saved aggregate evidence.

**Component readiness:**

| Component | Phase 7 status |
|---|---|
| Text/OCR cue screen | Working heuristic prototype; direct consumer validity unestablished. |
| Survey privacy × relevance/benefit profiles | Reproducible descriptive research; not operational targetable segments. |
| Financial comparison and scenario arithmetic | Implemented, input-validated, deterministic and unit-tested; economic predictions unestablished. |
| Minimum-change action and permission gates | Exploratory business rules; useful review prompts, not verified marketing effectiveness or legal compliance. |
| Added-variant or segment-targeting recommendation | Compared as options only; no automatic endorsement from current evidence. |
| Sentiment, visual understanding, product interest and ad–consumer matching | Unsupported by the present product/data. |
| Five-level personalization threshold | **`insufficient_evidence`**, unchanged. |

## 6. Files created or changed

**Created:** `baselines/phase7-start-2026-11-07/` (81-file copy and source-hash manifest); `phase7_segmentation.py`; `results/phase7_segmentation_v1.json`; `stp_advisory.py`; `test_phase7_stp.py`; `PHASE7_SEGMENTATION_EVIDENCE.md`; `PHASE7_STP_DECISION_LOGIC.md`; this `PHASE7_BUDGET_AWARE_STP_REPORT.md`.

**Modified:** `marketer_app.py` (optional strategy response), `web/index.html` (campaign form/advisory result), `web/app.js` (input/rendering), `web/app.css` (responsive styling), `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`.

**Not modified:** original datasets, prior results/reports, all NPZ models, survey/Criteo/UPAD experiment code, `intrusive_ad_model.py`, `threshold_engine.py`, and the research dashboard. No application restructuring or external campaign integration occurred.

## 7. Verification performed

- **Python regressions:** `python -m unittest discover -q` with the project's bundled `PYTHONPATH=.vendor` runtime: **59/59 passed** (the Phase 6 baseline was 48; eleven new strategy/financial/permission/API tests were added). These include missing inputs, budget overspend, break-even, negative scenario value, no rollout from hypothetical best case, multi-variant expense, unassessable images, consent/eligibility gates, objective warnings, invalid values, old API compatibility and threshold abstention.
- **Syntax:** `node --check web/app.js` and `web/research.js`; `py_compile` for the new modules and app: passed.
- **Segmentation reproducibility:** recomputing `phase7_segmentation.analyze()` matched the saved Phase 7 JSON **exactly**; the script's source hashes match the audited originals.
- **Preservation:** checkpoint comparison: 81 copied files, 74 unchanged, seven expected product/document edits, zero missing; seven original-source hashes unchanged; all previous research JSON and NPZ artifacts unchanged.
- **Threshold:** direct call to `current_dataset_status()` returned `insufficient_evidence`.
- **Real browser, not an in-process substitute:** Started the updated local server at `127.0.0.1:8768` and operated it in the ChatGPT in-app browser. A generic text ad with no finance inputs displayed low rubric tier **0/10**, **Keep current campaign**, unknown economic figures and threshold abstention. With “Last chance! Only 3 left!”, budget **1,000**, commitments **900**, revision cost **20**, variant/segmentation/management costs **80/50/30** and margin **12**, the page displayed moderate tier **4/10**, **Revise one creative**, **100** headroom, **2** break-even extra conversions and an **over-budget 160** one-variant option. Changing structured method to behavioural while permission remained unverified displayed **Hold for review**; hypothetical revision scenario 0/3/10 extra conversions rendered net **−20/+16/+100** without a rollout recommendation. The final server also showed **Hold for review** in the separate permission column for unverified broad-demographic targeting. Expanding the profile panel showed Gen Z 296 and Romano 837 with source-separated counts and a non-targetability warning. Entering existing CPC **5** and contribution margin **20** displayed both as **reported context**, explicitly without predicted uplift. At an explicit **390-pixel** viewport, `document.documentElement.scrollWidth` was **375**, less than `innerWidth` **390**; the option table scrolled within its container. The temporary viewport override was reset. A new image upload was **not** repeated in Phase 7; the unchanged OCR/creative code retains Phase 6's documented image-browser check and existing regressions. All monetary and performance figures in these browser interactions were **hypothetical test entries**.

These checks verify software behavior and preservation, **not** a causal improvement in campaign performance or a new external validation set.

## 8. Remaining limits and next evidence step

The current secondary sources do not jointly identify the same consumer, ad creative, consented targeting method/intensity, direct intrusion/relevance reaction and engagement outcome, with impressions and repeated observations. The two-axis survey profiles may reflect sampling bias and same-wave response style; they cannot be attached to the marketer's actual audience. Budget inputs are self-reported and do not establish causal uplift or margin stability. The app accepts CPC/CPM/conversion context but has no basis to extrapolate a new variant's performance or account for media reallocation. The permission gate is a conservative workflow prompt, not legal advice. Creative OCR misses visual content; no sentiment or object detector was added. The Criteo dataset's CC BY-NC-SA 4.0 terms also constrain commercial reuse of that separate research source.

**Next development step:** Investigate a specific, reusable secondary experiment or legitimate consented first-party pilot source that links creative and defined personalization treatment to direct intrusion/relevance responses and engagement on the **same exposure**, with denominator and held-out validation. Keep the current rule-based app and `insufficient_evidence` threshold boundary until that evidence exists. Do not tune survey models or multiply campaign variants in place of obtaining the missing joint measurements.
