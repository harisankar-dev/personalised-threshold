# 49-C final application completion

12 November 2026. Working academic demonstration. Synthetic outputs are not empirical consumer predictions.

## Run and demonstrate

Use the existing environment: `& 'C:\ProgramData\anaconda3\python.exe' marketer_app.py --no-browser --port 8774`, then open `http://127.0.0.1:8774/` in Chrome. The running demonstration is available there. Navigation connects Campaign planner, Consumer & levels, and Research evidence. Creative/campaign form values and simulation controls persist in session storage between pages; current campaign budget headroom is shared with the comparison. Images must be reselected after navigation; image data are not stored in browser storage.

## Delivered functionality

The existing campaign planner retains text/image uploads, local English Tesseract.js OCR, cue explanations, editorial 0–10 score, A–E STP options, permission review, budget headroom, break-even conversions and hypothetical financial scenarios. OCR results now include an editable transcript and Analyze corrected text action. The correction endpoint analyzes the edited text without reintroducing stale OCR, records original and corrected transcripts distinctly, and preserves the original quality warning in the UI. A discovered cue gap was fixed for exact/current viewer-location knowledge and present-tense tracking claims; seller contacts and negation remain covered by tests.

Consumer & levels provides individual fictional profiles, editable four-trait inputs, four synthetic segments with counts 100/75/76/49, discomfort and relevance estimates for all L0–L4 levels, response charts, data-source requirements, cost entry and transparent eligibility. Actual Gen Z (296) and Romano–Han (837) survey profile counts and existing bootstrap share intervals appear separately with source attribution. No unrelated records were joined.

L0 generic, L1 context/broad demographics, L2 browsing/search behavior, L3 purchase/relationship history and L4 combined sources are operational conceptual demonstration levels. The API validates finite 1–7 inputs. L2 requires behavioral data possession and permitted use; L3 requires historical data; L4 requires all three sources. Unknown permission holds the affected levels. Missing incremental costs or headroom prevents a financial feasibility claim. The demonstration selects the lowest-complexity eligible level meeting the user's maximum discomfort and minimum relevance, or abstains. Disclosures remain present across every comparison. Synthetic selections never enter the real STP decision or override its safeguards. The real evidence threshold remains `insufficient_evidence`.

## Synthetic model and separation

The supplied generator, CSV and README are preserved under `synthetic_demo/`; there are 300 fictional consumers and 1,500 exposures. `synthetic_demo/train.py` reproduces `model.json` using quadratic polynomial features and Ridge alpha 10. Inputs are four simulated pre-exposure traits, conceptual intensity and disclosure. IDs, generated segment labels and outcomes are excluded from features. All five rows of each fictional consumer remain together: 240 training and 60 test consumers. No feature preprocessing is learned from test outcomes. Model coefficients are synthetic-only and served with the standard-library application; runtime inference does not require scikit-learn.

| Synthetic test target, 1–7 | Model MAE | Model RMSE | Level-mean baseline MAE |
| --- | ---: | ---: | ---: |
| Discomfort | 0.5123 | 0.6665 | 0.7654 |
| Relevance | 0.6974 | 0.8698 | 0.8326 |

Discomfort MAE by L0–L4 is 0.389/0.409/0.600/0.577/0.586. Only three synthetic test exposures have discomfort ≥5; two are predicted below 5. This tiny extreme group supports no safety claim. No confidence intervals are invented. Synthetic segment outcomes are descriptive generated-data averages, not held-out segment predictions. Every synthetic output panel has the requested small Synthetic data label and explanatory hover text. Existing real research retains its original measurement scales and limits. These metrics demonstrate fitting the generator, not real-world generalization.

## Verification and preservation

- Full suite in `PYTHONPATH=phase12_validation/compat;.phase8_vendor` with Anaconda: **127 tests run; 126 passed; 1 skipped**. The optional Phase 12 source-archive audit is skipped because PHASE12_AD_CSV/PHASE12_AD_ZIP are unset; it is not counted as a pass. The R-backed SAV adapter is used; Windows security controls are unchanged.
- **21 real Chrome checks passed** using `final_browser_checks.cjs`: real ad image OCR, corrected-text privacy analysis, original OCR retention, seller-contact safety, individual and segment outputs, five levels, labels, real survey counts/attribution, unknown and denied permissions, L4 combined requirements, insufficient budget, real-threshold abstention, A–E options, 400 headroom from 1,000 minus 600, shared context, and narrow layout. Desktop/mobile screenshots were inspected; screenshots remain in ignored `.ocr_tmp`.
- Training replay exactly reproduced the final synthetic artifact, including baseline RMSE diagnostics. Source split/leakage, numerical bounds, missing inputs, segment counts, permissions, costs and threshold behavior have dedicated tests.
- All **604** originally protected research artifacts match their SHA-256 manifest. Historical real models/results and source datasets are unchanged. Pre-existing uncommitted `local_surveillance_v1.py` and its aggregate result were preserved and included as prior local research, not integrated into personal prediction.
- No real respondent rows, restricted workbooks, OCR logs or caches are part of this implementation. The fictional CSV is explicitly identified as synthetic.

## Changed files and limitations

Application changes: `marketer_app.py`, `synthetic_simulation.py`, `intrusive_ad_model.py`, `web/index.html`, `web/app.js`, `web/app.css`, `web/research.html`, `web/simulation.html`, `web/simulation.js`. Added synthetic generator/data/model/training assets, `test_synthetic_simulation.py`, `final_browser_checks.cjs`; expanded `test_english_ocr_privacy_repair.py`. This is the sole new completion report.

Source-specific research rights remain as previously documented. The empirical individual-discomfort and L0–L4 recommendation claims remain unsupported. OCR still requires human review; manually corrected results are not automatic OCR improvements. Permissions are marketer declarations, not independent legal verification. Budget arithmetic uses declared costs and does not forecast ROI or uplift. The application is a functioning academic demonstration, not a validated production audience-targeting service.
