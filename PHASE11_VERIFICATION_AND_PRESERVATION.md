# Phase 11 — verification and preservation

**9 November 2026.** Phase 11 tested the existing Mode A product and made only targeted rule, arithmetic and wording edits. No respondent-level research data were processed, no model was fitted, no Mode B customer upload was enabled and no campaign was published.

## Starting state and checkpoint

The `main` working tree was clean at Phase 10 commit `021aea8d1ecc764bc9e653998a4ea6f9c1ba4df6`. The recoverable local tag **`phase11-start-2026-11-09`** was created at that commit before edits. The Phase 9 preservation manifest returned `{"checked": 604, "errors": []}` before and after changes. No original dataset, saved research model/result, prior report, threshold engine or Phase 9/10 research intake file changed. The six synthetic diagnostics are separate from all source survey respondents.

## Python environment and executed tests

The established runtime is `C:\ProgramData\anaconda3\python.exe` (Python 3.14.6) with `PYTHONPATH=.phase8_vendor`. On this machine, Windows Application Control now blocks the existing `.phase8_vendor\pyreadstat\_readstat_parser` native DLL. This occurred **before Phase 11 edits** and persisted on an elevated baseline rerun. It is not attributed to Phase 11 code. No security control was bypassed or prior survey code changed.

| Executed check | Observed result |
| --- | --- |
| Pre-change complete `unittest discover -q` | **82 tests run, four errors**, all at the blocked `pyreadstat` import; 78 other tests completed. The earlier Phase 10 82/82 result is historical, not a Phase 11 baseline pass. |
| Final complete `unittest discover -q` | **90 tests run, the same four DLL import errors**; 86 other tests completed. No Phase 11 test failed. |
| Focused product/privacy/API/threshold suite | **69 tests, OK** (`test_phase11_product_validation`, `test_model`, `test_phase7_stp`, `test_phase8_compatibility`, `test_phase6_product`, `test_phase10_research_safeguards`, `test_threshold_engine`). |
| New Phase 11 synthetic product module | **8 tests, OK**, including a frozen creative comparison, 18 STP states, cost boundary and cent-precision cases. |
| `node --check web/app.js` | Passed. |
| Python `py_compile` of changed modules and validation scripts | Passed. |
| Direct threshold call | `status: insufficient_evidence`, `recommended_level: None`. |
| Phase 9 SHA-256 source/model/result audit | **604 checked, zero missing/changed**. |
| `git diff --check` before staging | Passed. |

The four unavailable tests are `test_direct_intrusion_items_are_the_target_only`, `test_answer_vector_groups_never_cross_partitions`, `test_cv_does_not_read_held_out_targets`, and `test_model_selection_excludes_calibration_and_outer_holdout_targets`. Their original saved results remain hash-protected, but their runtime behaviour could not be reverified in this environment. The failed full-suite status must not be presented as a complete pass.

## Real-browser checks

The local server was started at `127.0.0.1:8767` and exercised through a real browser. Observed: generic text 0/10; explicit surveillance 5 privacy points; pressure/discount text 6 pressure points; a negated quoted urgency phrase 0; the supplied aggressive PNG through local English OCR 12 pressure points capped at 10/10; a disposable blank PNG returning `needs_review` and no score; unknown targeting source and unverified behavioural consent both holding; a 10-headroom campaign holding a 20-cost revision and allowing a 5-cost revision; hypothetical positive scenario values remaining labelled as user-entered; overspent-budget error followed by successful corrected submission; singular “1 extra conversion” after reloading the changed JavaScript. The blank fixture was removed. At a 390 × 844 viewport, read-only geometry showed document width 375, primary control width 301 and no page-level horizontal overflow; the comparison table scrolls within its container. No marketer participants, usability scores or accessibility certification are claimed.

## Exact files changed

**Modified:** `intrusive_ad_model.py`, `stp_advisory.py`, `web/index.html`, `web/app.js`, `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`.

**Created:** `phase11_validation/creative_cases_v1.json`, `phase11_validation/creative_baseline_v1.json`, `phase11_validation/creative_after_v1.json`, `phase11_validation/evaluate_creative.py`, `phase11_validation/rubric_inventory.py`, `phase11_validation/rubric_inventory_v1.json`, `test_phase11_product_validation.py`, `PHASE11_CREATIVE_SCREENING_VALIDATION.md`, `PHASE11_STP_DECISION_RELIABILITY.md`, `PHASE11_BUDGET_STRESS_TEST.md`, `PHASE11_MARKETER_UX_AND_CLAIMS_AUDIT.md`, `PHASE11_PRODUCT_VALIDATION_SUMMARY.md`, and this report.

The only new evaluation rows are synthetic software fixtures without participant information. The Phase 10 staging guard **passed** before commit: 20 intended code, synthetic diagnostic, test and report paths were staged, with no restricted path. `git diff --cached --check` also passed. The final commit SHA, push result and clean/dirty Git status are recorded in the final handoff; `git log -1` identifies the committed Phase 11 state.
