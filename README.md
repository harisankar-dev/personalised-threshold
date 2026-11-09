# The Personalization Threshold: Predicting When Hyper-Personalized Advertising Becomes Intrusive (49-C)

**Implemented portfolio application:** Privacy-Aware Advertising Analytics, Creative Screening and Budget-Aware Pre-Launch Advisory  
**Research status:** secondary-data feasibility study. The five-level personalization threshold is **not validated**.

This project combines a local marketer-facing campaign planner with a separate research dashboard. The planner accepts ad text or an image, reads printed English text from images with local OCR, and flags observable privacy references and pressure tactics. It returns a low/moderate/high **screening tier**, an exploratory **0–10 rubric score**, matched cues, and editing suggestions. The score is not a probability, a consumer rating, or a statistically validated prediction of how a particular person will feel. An image with no matched cues abstains with `needs_review`.

Phase 9 checked the OSF location-targeting experiment's current data rights and privacy status, screened licensed alternatives, and preserved source/model/result hashes. **No new intrusion model was trained:** the OSF workbooks have no explicit dataset reuse license and include direct identifiers, while the licensed alternatives lack the required ad-specific intrusion × assigned-personalization linkage. See the [rights review](PHASE9_DATA_RIGHTS_AND_PRIVACY_REPORT.md), [experimental modelling decision](PHASE9_EXPERIMENTAL_INTRUSIVENESS_REPORT.md), [STP implications](PHASE9_STP_RESEARCH_IMPLICATIONS.md), [verification](PHASE9_VERIFICATION_AND_PRESERVATION.md) and [unsent permission draft](PHASE9_OSF_DATA_PERMISSION_REQUEST.md). The marketer application and its five-level abstention remain unchanged.

Phase 10 rechecked that source without downloading respondent records or contacting researchers. No source-specific permission for respondent-level modelling and derivative use was verified, so no new experimental model was trained. A separate fail-closed intake and synthetic safeguard tests prepare for a future authorized release. See [data eligibility and privacy](PHASE10_DATA_ELIGIBILITY_AND_PRIVACY_REPORT.md), [experimental analysis](PHASE10_EXPERIMENTAL_ANALYSIS.md), [model decision](PHASE10_INTRUSIVENESS_MODEL_REPORT.md), [STP implications](PHASE10_STP_RESEARCH_IMPLICATIONS.md) and [verification](PHASE10_VERIFICATION_AND_PRESERVATION.md). The marketer screen and five-level threshold are unchanged.

Phase 11 checked the **product's software and decision rules** with a frozen 26-case synthetic cue set, an 18-state STP matrix, financial stress tests and a real-browser walkthrough. The cue set is not independent consumer validation. Local denial handling, cent-precision money checks and several explanations were improved without changing the score weights or connecting new research data. See the [creative validation](PHASE11_CREATIVE_SCREENING_VALIDATION.md), [decision reliability](PHASE11_STP_DECISION_RELIABILITY.md), [budget stress test](PHASE11_BUDGET_STRESS_TEST.md), [UX/claims audit](PHASE11_MARKETER_UX_AND_CLAIMS_AUDIT.md), [summary](PHASE11_PRODUCT_VALIDATION_SUMMARY.md) and [verification](PHASE11_VERIFICATION_AND_PRESERVATION.md). Four survey tests are currently blocked by Windows Application Control on the existing `pyreadstat` DLL; the focused product suite passes.

Phase 8 adds a separate **consumer–ad evidence check** to the default research-informed planner. Marketers can declare a product category, channel and targeting data source; the app checks for source/method/permission conflicts and explains which consumer response measurements are still missing. It does **not** calculate a consumer-fit score or predict relevance, discomfort or conversions. An optional company-audience mode is **designed only**: `phase8_audience_contract.py` validates a strict schema offline, but the app has no customer-file upload or live audience analysis. The [compatibility report](PHASE8_CONSUMER_AD_COMPATIBILITY_REPORT.md), [secondary-evidence search](PHASE8_SECONDARY_EVIDENCE_SEARCH.md), [architecture](PHASE8_HYBRID_STP_ARCHITECTURE.md) and [verification report](PHASE8_VERIFICATION_REPORT.md) document the scope.

Phase 7 adds a **minimum-change advisory** beside the screen. Marketers may supply their campaign objective, declared targeting method, permission/eligibility status, total budget, committed spend, change costs and optional performance context. The planner always compares **keeping the existing campaign** with a single revision, a targeting adjustment and added variants. It calculates budget headroom, option cost, break-even extra conversions and optional *user-defined hypothetical* net-value scenarios when enough inputs are available. It never estimates uplift from these inputs or automatically recommends multiple campaigns. Two source-separated privacy × relevance/benefit survey profiles are shown as **research context only**, not targetable people.

The dashboard displays **saved aggregate results** from isolated secondary-data experiments. It never applies survey or Criteo models to an uploaded ad. The threshold decision engine remains `insufficient_evidence` because no available dataset measures direct intrusiveness and engagement for the five defined personalization levels on the same exposures.

## Start the application

Requirements: Python 3.11+ with the packages in `requirements-research.txt`; Node.js and `tesseract.js` 7.0.0 for image OCR; the existing `models/eng.traineddata` English language file. From the project directory:

```powershell
python -m pip install -r requirements-research.txt
npm install
python marketer_app.py
```

The app binds to `127.0.0.1` and opens `http://127.0.0.1:8765/`. If that port is occupied, run `python marketer_app.py --no-browser --port 8767` and visit the printed local URL. Text-only screening does not need OCR; image screening does. The current workspace already contains the language file and a bundled OCR dependency fallback. The app does not call a cloud AI service.

### Marketer walkthrough

1. Open **Campaign planner**. Paste the exact ad copy, or switch to **Image ad** and choose a PNG, JPEG, WebP, BMP, or TIFF file under 10 MB. You can also describe important visual details in text; the program does not recognize visual objects itself.
2. Supply the campaign objective, targeting method and permission/eligibility status if known. Enter your **total budget** and already committed spend for a headroom check; optional change costs, contribution margin and scenario conversions unlock break-even and what-if arithmetic. Blank inputs remain explicitly unknown. The total budget includes current commitments and new implementation costs; no media reallocation is assumed.
3. Press **Analyze ad**. Read the tier and **Creative Intrusiveness Screening Score — Exploratory (0–10)**, then the **Minimum-change plan**. The plan is an exploratory business-rule advisory. Its additional-conversion scenarios are entered by you, not predicted. A 0 on text means no current rule matched; it is not evidence of consumer comfort.
4. Review source-labelled **Exploratory consumer profiles** as unrelated survey descriptions only. The app cannot identify your audience members or predict which profile will respond. Read the **Personalization threshold** notice; it still recommends no level. Use **Research evidence** for the separate models and limitations.

For a short demonstration, try **Generic offer**, **Cart reminder**, and **Combined signals**. The supplied aggressive ad screenshot gives a high screening tier with a 10/10 displayed cap, driven by countdown, scarcity, extreme discount, urgency and alarmist copy. Its privacy cue total is 0; its pressure cue total is 12 before the display cap. That case is a regression example, not evidence of general accuracy.

## Architecture

| Layer | Files | Responsibility |
| --- | --- | --- |
| Local HTTP app | `marketer_app.py` | Serves the two browser pages and JSON endpoints; validates text/image input; uses temporary image files; binds to localhost. |
| Creative screen | `intrusive_ad_model.py`, `ocr_ad.cjs` | Local English OCR plus an explicit privacy/pressure cue rubric. No fitted consumer-intrusion classifier. |
| Browser UI | `web/index.html`, `web/app.js`, `web/app.css` | Accessible text/image workflow, cue explanations, error/loading states, responsive layout. |
| Research dashboard | `research_dashboard.py`, `web/research.html`, `web/research.js` | Reads **only saved aggregate JSON results** into separate, source-labeled research sections. No respondent pooling or live ML inference. |
| Survey profile audit | `phase7_segmentation.py`, `results/phase7_segmentation_v1.json` | Separate, source-hash-checked descriptive privacy × relevance/benefit quadrants; aggregate counts only. |
| Campaign advisory | `stp_advisory.py` | Validated financial arithmetic, conservative permission/eligibility gates and minimum-change business rules; no uplift predictor. |
| Threshold contract | `threshold_engine.py` | Defines Levels 0–4 and hard evidence/consent/risk gates; current data return `insufficient_evidence`. |
| Research experiments | `analysis.py`, `survey_phase_v*.py`, `criteo_*.py`, `ad_blockers_intrusion_v1.py`, `vietnam_privacy_trust_v1.py` | Versioned analyses using secondary sources. Research outputs are not application predictors. |

`POST /api/analyze` retains its previous result fields (`tier`, `score_out_of_10`, `privacy_score`, `pressure_score`, `evidence`, `recommendations`, `threshold_decision`, etc.). An optional `campaign` object adds a separate `strategy` response; omitting it retains the previous response shape. `GET /api/research` serves aggregate dashboard data; it sends no respondent records. Static routes are `/`, `/research`, `/app.css`, `/app.js`, and `/research.js`. See `PHASE7_STP_DECISION_LOGIC.md` and `PHASE7_BUDGET_AWARE_STP_REPORT.md` for the economics and evidence limits.

## Research evidence at a glance

| Component | Supported result | Important limit |
| --- | --- | --- |
| Original 49-C actions | On 49,940 user-disjoint held-out recorded actions, logistic click-versus-other-action AUC **0.499** versus constant **0.500**. | No useful gain, no non-action impression denominator, no intrusion labels. |
| Romano–Han unsolicited-social-ad survey | 837 respondents; 167 held out. General-ad intrusion MAE: training-mean **0.815**, V1 **0.521**, V2 **0.509** on a 1–7 target. | V2's gain interval includes zero; same-wave privacy/intrusion overlap and high-case false reassurance. |
| Independent Redondo–Aznar web-ad survey | 1,511 respondents; 302 held out. Within-source MAE **0.840** versus baseline **0.955**, on a −3 to +3 target. | Different scale and predictors; negative-intrusion subgroup MAE **2.528**. Not coefficient-level external validation of Romano–Han. |
| Criteo Uplift | 39,983 held-out rows. Binary-treatment visit prediction beats constant Brier baselines in both arms. | Uplift ranking gain interval includes zero; no intrusion or five-level treatment. |
| Vietnam online-market survey | 467 selected respondents; online trust/purchase-intention Spearman rho **0.450**. | Descriptive association, no ad or direct intrusion target. |
| Gen Z personalized-ad survey | 296 self-report records; perceived personalization/privacy rho **0.209**. | No assigned treatment or direct intrusion rating. |
| Marketer creative screen | Working, explainable text/OCR rubric and three tiers. | No calibrated accuracy against consumer ratings of these creatives. |
| Five-level threshold | Explicit evidence gate and `insufficient_evidence` outcome. | No scientifically valid recommendation from current secondary data. |

The dashboard links each source record and shows its saved result file. See `PHASE5_MODEL_VALIDATION_REPORT.md` for the full evidence matrix and extreme-error analysis, `THREE_DATASETS_EVALUATION_REPORT.md` for the supplied ZIP audit, and `PHASE6_PRODUCT_READINESS_REPORT.md` for the implementation and verification record. The Criteo source is **CC BY-NC-SA 4.0**; check its noncommercial/share-alike terms before reusing its data in an external product. The other named survey sources have their own licenses documented in the reports.

## Reproduce and verify

From the project root, with dependencies installed:

```powershell
python -m unittest discover -q
python -c "from phase6_preservation_audit import verify; print(verify())"
```

On the inspected Windows workspace, bare `python` points to Python 3.15 without the research packages. A verified full-suite command is:

```powershell
$env:PYTHONPATH = '.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
```

This uses the installed Anaconda environment and a project-local `pyreadstat` wheel. It passed **72 tests** on 8 November 2026. Package versions differ slightly from `requirements.txt`; see the Phase 8 verification report before claiming exact environment reproduction.

Saved experiment scripts intentionally refuse to overwrite their versioned outputs. To rerun research, use a **fresh copy** of the project or direct outputs to a new versioned destination. `results/phase6_repro_audit.json` records an exact replay of seven prior research experiments after the Phase 6 product edits. `results/phase6_preservation_audit.json` compares checkpoint hashes for research code, saved outputs, models, and selected original sources. `baselines/phase6-start-2026-11-07/` is the recoverable pre-change checkpoint. The full Criteo source archive is stored with Git LFS; clone with Git LFS enabled to retrieve it.

No primary survey or participant collection was performed. No unrelated survey respondents were joined, no five-level outcomes were invented, and no experimental survey model was promoted into the marketer screen.
