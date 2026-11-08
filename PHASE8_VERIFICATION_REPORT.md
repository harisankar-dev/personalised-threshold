# Phase 8 — verification, preservation and readiness

**49-C | 8 November 2026 | Project root:** `C:\Users\imhar\Desktop\amlbt`. All work used secondary sources. No participant collection, customer-file ingestion, live campaign action or model promotion occurred.

## 1. Baseline and recoverable checkpoint

`git status --short` returned **“not a git repository”**. Before product edits, `baselines/phase8-start-2026-11-08/` copied **87** code, documentation, web, saved-result and NPZ files. Its `manifest.json` records SHA-256 for every copy and **33** original source files in the project root and immediate local dataset directories. Raw sources were hashed, not duplicated into the checkpoint. The Phase 7 baseline contained the text/image rubric, 0–10 exploratory cue score, A–E budget options, source-separated survey personas, permission/eligibility gates and abstaining threshold. With the restored environment, the **pre-change complete suite passed 59/59**.

The read-only `phase8_preservation_audit.py` compared the final workspace with that manifest. **79/87** copied files still match byte-for-byte; the **eight** differences are exactly the intended app/documentation edits listed below. There are **zero** missing or unexpectedly modified checkpoint files, **zero** corrupted checkpoint copies, **zero** changes among the 33 hashed original source files and **zero** changes to saved `models/` or `results/` artifacts. The previous V1, V2, Criteo, Phase 4–7 reports and experiments remain in place. New Phase 8 files use separate names.

## 2. Reproducible Python command and environment limit

Bare `python` resolves to `C:\Python315\python.exe` (**3.15.1**) with only pip. On the initial Phase 8 recheck, `python -m unittest discover -q` ran 48 importable tests and reported **8 import errors** because NumPy/pandas and other research dependencies were missing. An attempt to install the pinned `requirements-research.txt` into the existing `.vendor` under Python 3.15 was stopped: the pinned NumPy 2.3.5 was offered as a source build, not a ready wheel for that interpreter. **No global Python installation was modified.**

The existing `C:\ProgramData\anaconda3\python.exe` (**3.14.6**) had NumPy, pandas, SciPy, scikit-learn and openpyxl, but no SPSS reader. The pre-existing `.vendor/pyreadstat` binary is tagged `cp312`, so it cannot load under Python 3.14. A compatible `pyreadstat==1.3.7` wheel was installed **only** in the new project-local `.phase8_vendor` directory with `--no-deps`. Verified versions:

| Component | Runtime used for full tests |
|---|---|
| Python | `C:\ProgramData\anaconda3\python.exe`, **3.14.6** |
| NumPy | **2.4.6** |
| pandas | **3.0.3** |
| SciPy | **1.18.0** |
| scikit-learn | **1.9.0** |
| openpyxl | **3.1.5** |
| pyreadstat | **1.3.7**, from `.phase8_vendor` |

Exact full-suite command from the project root:

```powershell
$env:PYTHONPATH = '.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
```

Result **before edits: 59 tests, OK. After final edits: 72 tests, OK.** The 13 new tests cover Mode A evidence labels/abstention, creative-versus-consumer response separation, source/method mismatch, unresolved personal data, no variant rollout from a hypothetical best case, invalid declarations, old/new API compatibility, Mode B field and permission validation, PII/unknown-field rejection, timestamps, duplicate events, ad IDs and absence of survey joins. `node --check web/app.js`, `node --check web/research.js` and Python compilation of changed/new modules passed. A direct threshold call returned `insufficient_evidence`.

**Reproduction limit:** `requirements.txt` still pins NumPy **2.3.5** and pandas **3.0.1**, whereas the pre-existing Anaconda installation has **2.4.6** and **3.0.3**. This is a passing, explicitly versioned local test environment, **not** bit-for-bit reproduction of the original dependency lock. The local wheel was obtained from the public package registry and is kept separate from research sources; installing it on another machine requires normal package/network access. The original `.vendor` and global Anaconda packages were not overwritten. Research scripts that write versioned outputs were not rerun against their prior saved artifacts in this phase; their code, data and artifacts are hash-preserved.

## 3. Real browser checks

The updated local app was started at `http://127.0.0.1:8770/` and operated in the ChatGPT in-app browser; these are **browser interactions**, not only HTTP unit-test simulations.

| Browser input or state | Observed result |
|---|---|
| Generic text, no financial data, generic method and no audience data | Low heuristic tier **0/10**, keep current campaign, unknown economic figures, visible evidence check stating consumer response unknown, threshold abstention. |
| Pressure text, behavioural method, first-party browsing source, permission/eligibility unverified, budget 1,000 and commitments 900 | Moderate cue tier **4/10**, **hold for review**, 100 budget headroom, source/permission check distinct from creative cues. |
| Same method with permission and eligibility marked verified, but data source left unspecified, after final server restart | **Hold for review** with explicit unresolved-source explanation; a declared permission value did not silently approve unknown data provenance. |
| User-supplied 6.95 MB aggressive ad screenshot in image mode | Local OCR found countdown, scarcity, 99% discount, urgency, alarmist copy and repeated exclamation cues; high heuristic tier **10/10**, one-creative revision advice, no consumer-fit prediction. Image objects/layout were not independently understood. |
| Budget 100, commitments 200 | Inline error: committed spend cannot exceed total budget; no result shown. Changing commitments to 50 cleared the error and produced a normal result. |
| Expand research profiles | Two visibly separate surveys: Gen Z **296** and Romano–Han **837** respondents, with a non-targetability warning. A displayed Gen Z percentage was corrected to use **exact count ÷ respondents**; 33/296 now shows **11.1%**. |
| Narrow viewport at **390 × 844** with uploaded long filename and result table | `document.documentElement.scrollWidth` **375** versus `innerWidth` **390** after the CSS fix; option table scrolls internally (**490** content versus **301** container). The temporary viewport override was reset. |

The page was cleared and left open for the user. No customer-file control or operational Mode B claim appears. These checks establish UI behaviour on specified fixtures, **not** population accuracy or a marketing effect.

## 4. Files created or modified

**Created:** `baselines/phase8-start-2026-11-08/` and its manifest; `.phase8_vendor/` containing the compatible project-local SPSS reader; `phase8_compatibility.py`; `phase8_audience_contract.py`; `phase8_preservation_audit.py`; `test_phase8_compatibility.py`; `PHASE8_CONSUMER_AD_COMPATIBILITY_REPORT.md`; `PHASE8_SECONDARY_EVIDENCE_SEARCH.md`; `PHASE8_HYBRID_STP_ARCHITECTURE.md`; this report. No OSF respondent-level file or trained Phase 8 model was saved.

**Modified, exactly eight checkpointed files:** `marketer_app.py` (separate compatibility response for campaign requests), `stp_advisory.py` (data-source review gate), `web/index.html` (three context fields and evidence panel), `web/app.js` (input and evidence rendering, exact profile percentages), `web/app.css` (long-filename mobile fit), `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`. `intrusive_ad_model.py`, `threshold_engine.py`, prior model code, saved model arrays and research dashboard were not changed.

## 5. Readiness and remaining risk

| Component | Final Phase 8 status |
|---|---|
| Mode A text/image screening | **Working heuristic prototype**; OCR and regex limitations; 0–10 is not consumer-rated discomfort. |
| Mode A compatibility evidence check | **Implemented descriptive/review workflow**; no numerical fit or audience prediction. |
| A–E budget comparison and permission/source gate | **Implemented and regression tested**; inputs are declared and uplift remains unknown. |
| Survey profiles | **Reproducible separate descriptive research**; cannot identify the marketer's customers. |
| New OSF location experiment | **Promising inspected source**, 409 + 401 lab respondents and four field ad-set aggregates; raw license/privacy and transfer issues block model retention/promotion. |
| Mode B | **Designed, with an offline schema validator tested on software fixtures only**. No real customer-data upload or behavioural demonstration. |
| Consumer-level fit/engagement uplift and five-level threshold | **Unsupported**; threshold still returns `insufficient_evidence`. |

The next evidence-backed step is to obtain explicit reuse rights and a minimized version of the linked OSF experiment, or another licensed source with the same outcome linkage. A narrowly scoped location-stimulus intrusion model could then be tested on untouched respondent/ad groups, against a simple baseline with high-case false-reassurance and subgroup uncertainty reported. It must stay research-only until transfer to other creatives and audiences is demonstrated. No paper's three stimulus conditions can be interpolated into the 49-C five-level threshold.
