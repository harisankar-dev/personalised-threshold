# Phase 10 — verification and preservation

**Status, 8 November 2026:** rights gate closed; no OSF respondent processing or new experimental model. This record separates measured verification from the prospective research protocol.

## Recoverable start and environment

The repository was clean at starting commit `1f37d9c2f0f489b0a86dc14946e642565585c530` on `main`. Before editing, a local Git checkpoint tag `phase10-start-2026-11-08` was created at that commit. A separate checkout can use that tag to recover the Phase 9 state without resetting the current working tree. The Anaconda environment was Python **3.14.6**, with the existing `.phase8_vendor` on `PYTHONPATH`. The pre-change complete suite ran **74 tests, OK**. The Phase 9 SHA-256 manifest verified **604 source/model/result files, zero errors** before changes.

## Changes in this phase

**Created:** `phase10_research/__init__.py`, `phase10_research/intake.py`, `phase10_research/staging_guard.py`, `phase10_research/rights_status.json`, `test_phase10_research_safeguards.py`, and the five `PHASE10_*.md` reports (data eligibility/privacy, experimental analysis, intrusiveness model, STP implications, verification/preservation).

**Modified:** `.gitignore`, `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`.

**Untouched:** original source files, saved `models/` and `results/`, V1/V2/Criteo/UPAD research, prior phase reports, `marketer_app.py`, `intrusive_ad_model.py`, `threshold_engine.py`, `stp_advisory.py`, `phase8_compatibility.py`, `phase8_audience_contract.py` and `web/`. No model artifact or research row export was created. The Phase 9 permission email remains a historical **unsent** draft; Phase 10 sent no message or contact request.

## Research and product safeguards

The actual `rights_status.json` blocks intake. Tests use only synthetic records. They cover source-specific rights scope, approved-column allowlist and identifier omission, quasi-identifier rejection, post-exposure predictor leakage, study-specific targeting coding, invalid/missing ratings, duplicate responses, respondent-disjoint splits, Git ignore and staged-path detection. This validates code behaviour on fixtures, not actual OSF data quality or authorization. The in-memory helper rejects missing/out-of-range core fields; no missingness estimate was computed in Phase 10. The earlier Phase 8 study counts and condition summaries are cited as prior observations, not new Phase 10 effects.

The marketer app and API were not changed, so a fresh browser session would not test a Phase 10 product change. Existing API, financial arithmetic, threshold and preservation regressions remain in the full suite. The research-only module is not imported by the live app. The threshold must still return `status: insufficient_evidence` and `recommended_level: None` for the current project evidence.

## Final verification record

| Check | Result |
| --- | --- |
| Phase 10 synthetic safeguard tests | **8 tests, OK** |
| Full regression suite after edits | **82 tests, OK**, 4.167 seconds; baseline was 74 |
| Phase 9 source/model/result SHA-256 manifest | **604 checked, zero errors** |
| Direct threshold status | `insufficient_evidence`, `recommended_level: None` |
| Application-file diff against checkpoint | No changed paths in the named app, advisory, compatibility, threshold or `web/` files |
| Restricted staged-file guard and staged review | **Passed**: only 14 intended code/documentation/test/ignore files staged; no restricted path; `git diff --cached --check` clean |
| Git commit and push | Exact final SHA and remote status are recorded in the final handoff; `git log -1` identifies this Phase 10 repository state |

The current research conclusion is stable regardless of test outcome: public OSF access and a data-availability statement do not establish every intended downstream use. Without reviewed rights and privacy-safe source records, no Phase 10 effect estimate, holdout metric, consumer model or five-level recommendation may be claimed.
