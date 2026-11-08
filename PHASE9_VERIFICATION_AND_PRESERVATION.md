# Phase 9 — verification and preservation record

**49-C | 8 November 2026 | Final status: research-data gate closed, app preserved.** The project used secondary sources only. No OSF respondent file, new participant response, trained experimental model, customer upload or campaign action was created.

## Recoverable starting point

The project was a **clean Git repository** on `main` before Phase 9, unlike the pre-Git status described in older reports. Its starting commit was `19c04024c16f0e92debc5b7eb7fa88b95b0d6486`. Before changing a project file, I created the local Git checkpoint tag **`phase9-start-2026-11-08`** at that commit. A recovery command is `git switch --detach phase9-start-2026-11-08` in a separate checkout; do not reset a working tree with uncommitted work. Earlier `baselines/` checkpoints and all Phase 1–8 reports remain present.

The separate [SHA-256 manifest](phase9_research/source_artifact_manifest.json) lists **570 tracked research-source files, eight saved-model files and 26 saved-result files**, total **604**. [The audit script](phase9_research/preservation.py) streams each file, refuses to overwrite its original manifest, and reports missing or changed entries. The first write and final verification returned `{"checked": 604, "errors": []}`. This includes the original Criteo archive, local survey files, user-supplied data copies, prior NPZ/model files and saved result outputs. The raw sources were hashed in place, **not duplicated** into a new checkpoint. Git preserves the full starting code/report/app state; the manifest adds SHA-256 integrity checks for research evidence. The nested CHI-ad source directory remains locally intact and is not changed by this phase.

## Environment and tests actually run

The full suite used **`C:\ProgramData\anaconda3\python.exe` (Python 3.14.6)** with the existing project-local `.phase8_vendor` on `PYTHONPATH`; the same runtime documented in Phase 8. The command was:

```powershell
$env:PYTHONPATH = '.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
```

| Check | Observed result |
|---|---|
| Baseline before changes | **72 tests, OK**. |
| New `test_phase9_preservation` focused run | **2 tests, OK**. It verifies the actual source/model/result manifest and detects a deliberately changed fixture. |
| Final complete suite after changes | **74 tests, OK**, 3.907 seconds on the final run. |
| Explicit manifest audit | **604 checked, zero missing/changed**. |
| Direct `threshold_engine.current_dataset_status()` call | `status: insufficient_evidence`; `recommended_level: None`. |
| Git diff against the starting tag for `marketer_app.py`, `stp_advisory.py`, `phase8_compatibility.py`, `phase8_audience_contract.py`, `intrusive_ad_model.py`, `threshold_engine.py` and `web/` | **No changes** (`git diff --quiet` exit 0). |
| Real browser recheck | **Not performed**: no application code, UI or route changed in Phase 9. Phase 8 browser evidence is retained, not presented as a Phase 9 execution. |

An initial new-test run failed because Python's default temporary directory was outside the filesystem sandbox. The fixture was changed to create its temporary directory inside the project root, with an explicit resolved-path containment assertion; the focused and full reruns above passed. This was a test-environment issue, not a research-data or app failure.

## What was implemented

**Created:** `phase9_research/preservation.py`, `phase9_research/source_artifact_manifest.json`, `phase9_research/candidate_matrix.csv`, `test_phase9_preservation.py`, `PHASE9_DATA_RIGHTS_AND_PRIVACY_REPORT.md`, `PHASE9_EXPERIMENTAL_INTRUSIVENESS_REPORT.md`, `PHASE9_STP_RESEARCH_IMPLICATIONS.md`, `PHASE9_VERIFICATION_AND_PRESERVATION.md`, and `PHASE9_OSF_DATA_PERMISSION_REQUEST.md` (an **unsent draft**).

**Modified:** `README.md`, `PROJECT_STATUS.md` and `CHANGELOG.md` to state the current research gate and link the deliverables. **Not modified:** original datasets, existing `models/` and `results/`, V1/V2/Criteo/UPAD experiment code, prior reports, marketer application, research dashboard, Mode B validator and threshold engine. No separate Phase 9 model artifact exists because no eligible training data was verified.

The [candidate matrix](phase9_research/candidate_matrix.csv) documents seven source decisions. OSF currently has no explicit data license or minimized workbook; its original lab exports include identifiers. The other licensed sources fail the joint direct-intrusion × assigned-personalization measurement requirement. The prospective modelling protocol is documented without fitting, opening a holdout, inventing high-intrusion false-reassurance counts or relabelling treatment arms. The published article's qualitative findings are attributed to its authors rather than counted as 49-C validation.

## Readiness and blockers

| Component | End-of-Phase-9 status |
|---|---|
| Existing Mode A creative screen, compatibility review and A–E budget planner | Operational **heuristic/advisory prototype**, preserved; not empirically validated for arbitrary consumer response. |
| Mode B | Offline schema validator only; no real customer upload or operational audience inference. |
| Romano–Han/Redondo surveys, Gen Z/Vietnam descriptions, UPAD and Criteo | Prior **separate research** preserved with their source-specific limitations; no cross-dataset consumer join. |
| Narrow location-targeting `PPI` model | **Blocked** until explicit reuse/derivative terms and privacy-safe respondent data are verified. No held-out metrics. |
| Five-level personalization threshold | **Unsupported**; returns `insufficient_evidence`. |

The next external dependency is author clarification or an explicitly licensed, identifier-minimized comparable dataset. The [permission email](PHASE9_OSF_DATA_PERMISSION_REQUEST.md) remains unsent for owner review. If rights and data quality later pass the gate, only the study-specific research protocol should be implemented first; new creative-family and audience validation would still be needed before product integration.
