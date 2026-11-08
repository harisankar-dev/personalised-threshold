# Phase 6 — product integration, dashboard and portfolio readiness

**49-C | 7 November 2026 | Secondary data only**  
**Implemented product:** Privacy-Aware Advertising Analytics and Creative Intrusiveness Screening  
**Research objective:** The Personalization Threshold: Predicting When Hyper-Personalized Advertising Becomes Intrusive

## 1. Original state and preservation

Phase 5 had 41 passing regression tests, seven reproducible research outputs, a functioning local marketer page, saved V1/V2/V3/Criteo/independent-survey/Vietnam results, and an abstaining five-level threshold. The page already accepted text and images, but its result heading could imply empirically validated intrusion risk; its separate research evidence was available only in reports. The server accepted arbitrary JSON field types by coercion, silently truncated long fields, trusted image MIME declarations, and could expose raw internal exception text. There was no top-level setup guide or research dashboard.

The project uses a Python standard-library `ThreadingHTTPServer`, static HTML/CSS/JavaScript, a rule-based creative screen, local Tesseract.js OCR, NumPy/pandas research scripts, and saved JSON/NPZ artifacts. **No Git repository exists** at this path, so no Git diff was available. Before modification, `baselines/phase6-start-2026-11-07/` saved **68** code/document/JSON/model files plus SHA-256 entries for **four** selected original sources. The preserved original datasets and models were not overwritten. The checkpoint and subsequent hash audit make the changes recoverable.

## 2. Product changes

### Creative-screen user experience

- Reframed the page around **creative review** and labeled the output **“Creative Intrusiveness Screening Score — Exploratory (0–10)”**. Tier labels now say low/moderate/high **screening tier**. The page explicitly says the number is a qualitative cue rubric, not a probability, consumer rating, or validated prediction.
- Added a visible summary of the analyzed text/image filename, OCR excerpt, optional visual description and whether targeting information was supplied. Matched phrases now identify whether they came from ad copy, targeting details, or image OCR/user description. All displayed user content is assigned with `textContent`, not HTML insertion.
- Improved English text/OCR instructions and made the visual-description limit explicit. Added loading `aria-busy`, clearer empty/error states, prominent threshold context, and links between the creative screen and research evidence.
- Kept the existing scoring rules, API response fields, examples, repair suggestions, zero-cue image abstention, and `insufficient_evidence` threshold behavior. No trained model was integrated into the screen.

### Research dashboard

Added `/research` and aggregate-only `/api/research` within the existing architecture. `research_dashboard.py` reads saved result files and exposes selected, source-labeled figures. The page separates:

1. **Engagement:** original 49-C recorded-action model versus constant baseline, and Criteo binary-treatment visit models and uncertain uplift ranking.
2. **General-ad intrusion:** Romano–Han V1/V2 versus baseline, same-wave privacy overlap, high-intrusion false reassurance, reused-holdout interval coverage, and a **separate** independent web-ad survey with its negative-response error.
3. **Privacy and trust:** Vietnam and Gen Z correlations as descriptive associations only, with sample and measurement limits.
4. **Threshold:** the five conceptual Levels 0–4, all without validated response estimates; required evidence and the live engine's `insufficient_evidence` status.

Each source is identified by saved JSON filename and linked to its publisher record. The dashboard does not combine incompatible metrics, pool respondents, infer causal effects, or claim the marketer app runs these research models. On a 390-pixel browser viewport the research cards form one column, levels form two columns, and document width remains within the viewport.

### Request validation and error recovery

`marketer_app.py` now requires a JSON object and string fields, rejects empty ad content and over-limit text rather than truncating, checks the allowed image type and actual file signature, rejects empty/over-10-MB images, and returns a **413** response for an oversized body. It responds with concise 400/422/500 errors without exposing raw OCR exception text. Image bytes remain in a temporary local folder during OCR and are removed afterward. The local server still binds to `127.0.0.1`; it does not send ads to a cloud API or log request contents.

The browser clears a previously selected image when a new upload is invalid, preventing stale-file analysis. Its form shows actionable errors and successfully accepts a new submission after an error. These checks reduce accidental or malformed input; file signatures alone do not constitute complete malicious-file detection.

## 3. Verified research evidence displayed

| Component | Verified saved figure | Readiness |
| --- | --- | --- |
| Original actions | 49,940 user-disjoint holdout actions; AUC logistic **0.499** vs constant **0.500** | Research feasibility result only |
| Criteo visits | 39,983 feature-vector-disjoint holdout rows; control Brier **0.02669** vs **0.03717** constant; treatment **0.03309** vs **0.04603** | Separate engagement benchmark; uplift interval crosses zero |
| Romano–Han intrusion | 837 respondents, 167 holdout; MAE baseline **0.815**, V1 **0.521**, V2 **0.509**; V2 predicted below 5 for **25/126** high cases vs V1 **18/126** | Experimental general-ad survey models |
| V3 uncertainty | 90% two-sided interval covered **149/167** overall, **5/10** below-neutral; upper bound below 5 for **6** high cases | Experimental, reused holdout; not a deployment guarantee |
| Independent web-ad intrusion | 1,511 respondents, 302 holdout; MAE **0.840** vs baseline **0.955**; negative group MAE **2.528** (n=26) | Different scale/source; separate benchmark only |
| Vietnam / Gen Z | Trust–purchase-intention rho **0.450** (n=467); perceived-personalization/privacy rho **0.209** (n=296) | Descriptive associations only |
| Uploaded ad creative | Cue rubric, OCR and 0–10 display cap | Operational prototype; unvalidated against consumer ratings |
| Personalization Levels 0–4 | `recommended_level: null`; `status: insufficient_evidence` | Unsupported recommendation; honest abstention |

The V1/V2 holdout has been examined across phases. Privacy and intrusion answers are contemporaneous, and the two intrusion surveys use different constructs/scales. The dashboard reports these limits beside the corresponding figures. No new model was fitted in Phase 6.

## 4. Software verification

**Focused tests:** `test_phase6_product.py` checks required ad content, field types/limits, spoofed and malformed image data, supported signatures, the aggregate dashboard's separate populations and abstaining threshold, the static/dashboard routes, output-schema compatibility, malformed JSON and server-side content/size errors. The route tests invoke the actual request handler in-process; the test runner's restricted network context does not permit a loopback socket. Their output is not described as browser verification.

**Actual browser test:** The updated server was started on `127.0.0.1:8767` and tested in the ChatGPT in-app browser. Observed outcomes:

| Browser action | Observed result |
| --- | --- |
| Startup and main page | New creative page and two-page navigation rendered. |
| Empty text and empty image submissions | Focused form errors: “Paste ad copy to analyze” and “Choose an image or add a visual description.” |
| Generic text ad | Low screening tier, **0/10**, input summary, threshold abstention. |
| Privacy plus pressure text | High screening tier, **10/10** display cap with six matched cues and editing suggestions. |
| Supplied aggressive PNG (6.95 MB) | High screening tier, **10/10**, privacy cue points **0**, pressure cue points **12**; OCR matched countdown, scarcity, 99% off, urgency, alarmist copy and repeated exclamations. Image-object limitation remained visible. |
| Unsupported `.txt` upload | Rejected with supported-type guidance; prior selected image cleared. |
| Synthetic >10-MB `.png` upload | Rejected with under-10-MB guidance. |
| Corrupt `.png` upload | Server rejected type/signature mismatch; no raw server exception displayed. |
| Recovery | Removing the corrupt file, switching to text, and resubmitting succeeded. |
| Research dashboard | All four sections rendered figures directly from `/api/research`, kept sources separate, displayed Levels 0–4 and `insufficient_evidence`. |
| 390-pixel viewport | Single-column cards, two-column levels, no horizontal document overflow (`scrollWidth` 375 at `innerWidth` 390). Viewport override was reset. |

The test image came from the user's previously supplied aggressive-ad example; the synthetic oversize/corrupt browser assets were removed after testing. Port 8765 was occupied by an older local process during this session, so final browser verification used fresh port 8767. Direct read-only HTTP checks on that port also returned 200 for `/research` and `/api/research`. No page or model claim rests solely on in-process tests.

**Research replay and preservation:** Seven saved experiments were rerun into `results/phase6_repro_audit.json` and matched their saved outputs and model arrays. `phase5_repro_audit.py` was updated only to recognize the known Phase 6 product-file edits; the replay comparisons were unchanged. `phase6_preservation_audit.py` compares the Phase 6 checkpoint hashes to current files and confirms research scripts, saved outputs, model artifacts and the four selected original sources remain unchanged. Final counts appear below.

## 5. Files created or modified

**Created:** `README.md`; `PHASE6_PRODUCT_READINESS_REPORT.md`; `research_dashboard.py`; `web/research.html`; `web/research.js`; `test_phase6_product.py`; `phase6_preservation_audit.py`; `baselines/phase6-start-2026-11-07/`; `results/phase6_repro_audit.json`; `results/phase6_preservation_audit.json`.

**Modified:** `marketer_app.py` (input validation and dashboard routes); `web/index.html`, `web/app.js`, `web/app.css` (UI, transparency, accessibility and responsive dashboard styles); `phase5_repro_audit.py` (known-product-edit allowlist for post-Phase-5 replay); `PROJECT_STATUS.md`; `CHANGELOG.md`.

No original dataset, NPZ model, prior result JSON, creative-scoring rule, threshold-engine decision code, or V1/V2/Criteo research implementation was changed. The checkpoint is the recovery path for every pre-existing edited file.

## 6. Reproduce and readiness

Use `README.md` for setup, architecture and walkthrough. In a Python environment with `requirements-research.txt` and `PYTHONPATH` including `.vendor` where pyreadstat is bundled, run `python -m unittest discover -q`. The two pages are `/` and `/research` on the local server. To inspect preservation without overwriting its versioned report, import and call `verify()` from `phase6_preservation_audit.py`. Research experiment scripts protect their saved outputs; rerun on a fresh project copy or with a new result path.

**Final regression and hash-audit counts:** **48/48** Python regression tests passed (41 pre-Phase-6 plus seven focused product tests). `node --check` passed for both browser scripts. The preservation manifest contains **72** entries: **65 unchanged** and **seven intentional product/documentation edits**, with **zero unexpected changes or missing files**. Four selected original source hashes, all checkpointed research code/result JSONs, and all checkpointed NPZ model files match. The seven research experiments reproduced exactly in the post-change replay. This verifies unchanged saved research; it does not create a fresh independent validation sample.

| Component | Final readiness |
| --- | --- |
| Marketer interface | **Usable local prototype** for explainable text/OCR cue screening, subject to stated language/vision limits. |
| Research dashboard | **Usable evidence viewer** of saved aggregate experiments, with separated sources and uncertainty. |
| Original event/Criteo models | **Research benchmarks** for action/visit outcomes only. |
| Survey intrusion models | **Experimental** general-ad response predictors; high/low tail and transfer limitations. |
| Vietnam/Gen Z studies | **Descriptive** consumer-context analyses. |
| 0–10 creative score | **Exploratory rubric**, without calibrated consumer-intrusion accuracy. |
| Five-level threshold | **Unsupported recommendation; `insufficient_evidence`** until compatible per-level response evidence exists. |

This is a portfolio-ready demonstration of dataset auditing, guarded model comparison, uncertainty-aware research communication, explainable screening and local full-stack development. It does not establish a scientifically validated individual personalization threshold.
