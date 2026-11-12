# 49-C · The Personalization Threshold

### Privacy-aware advertising analysis and personalization simulation

A local application for reviewing advertising copy, exploring consumer profiles, and comparing campaign changes against data permissions and budget constraints.

49-C brings together **creative screening**, **editable English image OCR**, **synthetic L0–L4 simulations**, and **budget-aware STP decision support**. A separate research dashboard presents findings from secondary datasets with their original sources and measurement scales.

**Project status:** working academic demonstration. Individual discomfort estimates and five-level comparisons use clearly labelled synthetic data. The empirical personalization threshold remains `insufficient_evidence`.

## What you can do

| Feature | What it provides |
| --- | --- |
| Advertisement review | Paste one ad or upload an image; inspect privacy references and advertising-pressure cues. |
| English OCR correction | Extract printed text locally, edit the transcript, and analyze the corrected copy while retaining the original OCR output. |
| Individual simulation | Enter four fictional consumer characteristics and compare simulated discomfort and relevance across L0–L4. |
| Consumer segmentation | Explore four synthetic privacy/relevance profiles alongside source-attributed profiles from real surveys. |
| Level recommendations | Apply explicit permission, cost, discomfort and relevance criteria; choose the simplest eligible simulated option or abstain. |
| Campaign planning | Compare keeping the campaign, revising a creative, adjusting targeting, or testing additional variants. |
| Research evidence | Inspect saved aggregate results, baseline comparisons, uncertainty and documented limitations. |

## Quick start

### Requirements

- Python with the packages in `requirements-research.txt`; the inspected development environment uses Python 3.14.6.
- Node.js and npm for image OCR; the inspected environment uses Node 24.
- The English language file at `models/eng.traineddata`.
- A modern browser.

```powershell
git clone https://github.com/harisankar-dev/personalised-threshold.git
cd personalised-threshold

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-research.txt
npm install

python marketer_app.py
```

Open **http://127.0.0.1:8765/**. The server binds to localhost and normally opens the browser automatically.

To choose another port:

```powershell
python marketer_app.py --no-browser --port 8774
```

The existing Windows development environment can run the app directly with:

```powershell
& 'C:\ProgramData\anaconda3\python.exe' marketer_app.py --no-browser --port 8774
```

The large historical Criteo archive uses Git LFS. Retrieving that research archive is not required for the browser demonstration, which uses saved aggregate research results and the included synthetic model artifact. Image OCR needs Node, `tesseract.js` and the local English language file. Ad content is processed locally without paid APIs or cloud OCR.

## A five-minute demonstration

1. **Review a creative.** In Campaign planner, paste one advertisement or upload a supported image under 10 MB. Analyze only the creative copy, rather than an entire explanation containing multiple ads.
2. **Correct OCR if needed.** Open the extracted-text section, edit the transcript and select **Analyze corrected text**. The analysis uses the revised text; original OCR and its quality warning remain available.
3. **Add campaign context.** Enter targeting details, permission status, total budget, committed spend and known implementation costs. Inspect the creative cues and A–E campaign options.
4. **Explore a consumer.** Open **Consumer & levels**, choose a fictional individual or segment, and set maximum simulated discomfort and minimum relevance.
5. **Compare all five levels.** Confirm which data you possess and may use, enter costs, and select **Compare L0–L4**. Missing permissions, costs or budget information prevent unsupported eligibility claims.
6. **Inspect the evidence.** Open Research evidence for real-data findings. Those results are kept separate from the fictional consumer simulation.

Campaign inputs persist within the browser session, and current campaign headroom is shared with the simulation. Images must be reselected after navigation; their contents are not stored in browser session storage.

## The five conceptual personalization levels

| Level | Approach | Data considered in the demonstration |
| --- | --- | --- |
| **L0** | Generic | No individually tailored targeting |
| **L1** | Contextual or broad demographic | Content context or broad demographic information |
| **L2** | Behavioral | Browsing, search or interaction history |
| **L3** | Historical | Prior purchases or customer relationship history |
| **L4** | Combined / hyper-personalized | Context, behavioral and historical sources together |

These are project-defined categories, not five conditions validated by the real research datasets. Increasing complexity does not guarantee increasing discomfort for every consumer.

The simulation checks data possession and permitted use for each required source. Unknown permission holds the affected level for review; L4 requires every combined source. Costs must fit known headroom. Among eligible levels meeting the user's stated simulated response criteria, the demonstration chooses the lowest-complexity option. Otherwise it abstains. Mandatory disclosures remain present across comparisons.

## Understand the outputs

| Output | Meaning |
| --- | --- |
| **Creative screening score, 0–10** | An editorial rule rubric for observable privacy and pressure cues. It is not a consumer rating or probability. |
| **Synthetic discomfort / relevance, 1–7** | A model or descriptive segment result derived from generated fictional consumers. Synthetic outputs carry a small **Synthetic data** label. |
| **Real research profiles** | Separate, descriptive survey groups with actual counts, source attribution and existing uncertainty estimates. They are not automatically targetable audiences. |
| **Budget and break-even figures** | Arithmetic using marketer-entered costs and margins. Economic scenarios are explicitly hypothetical. |
| **Empirical threshold** | `insufficient_evidence`; no validated L0–L4 recommendation for actual people is claimed. |

The synthetic recommendation never overrides the real campaign advisor's permission or financial safeguards. Perceived surveillance, general intrusiveness, click intention and observed conversion remain distinct research outcomes.

## Synthetic model

The supplied generator creates **300 fictional consumers × five levels = 1,500 exposures**. A quadratic feature expansion with Ridge regression predicts simulated discomfort and relevance from privacy concern, tracking awareness, relevance preference, personalization preference, conceptual intensity and disclosure.

The split keeps all five records for a consumer together: **240 training consumers and 60 test consumers**. Consumer IDs, generated segment labels and outcomes are excluded from the input features.

| Synthetic holdout target, 1–7 | Model MAE | Model RMSE | Level-mean baseline MAE |
| --- | ---: | ---: | ---: |
| Discomfort | 0.512 | 0.667 | 0.765 |
| Relevance | 0.697 | 0.870 | 0.833 |

These metrics measure learning of the generator's assumed relationships. They do not demonstrate accuracy on real consumers. Only three held-out synthetic exposures have discomfort ≥5; two receive predictions below 5, so high-discomfort reliability is not established. The UI does not invent individual confidence intervals.

To reproduce the artifact with the existing research environment, install scikit-learn if needed and run:

```powershell
python -m pip install scikit-learn==1.9.0
python synthetic_demo/train.py
```

Training reads only `synthetic_demo/exposures.csv`. The standard-library simulation runtime reads the saved coefficients; it does not require scikit-learn. Generator assumptions and the original synthetic-data documentation are in [`synthetic_demo/`](synthetic_demo/).

## Campaign decisions

The STP advisor retains five options:

- **A:** Keep the current campaign.
- **B:** Revise one creative.
- **C:** Adjust targeting within the campaign.
- **D:** Test one extra variant.
- **E:** Consider multiple variants when justified.

It calculates headroom, incremental implementation costs and break-even additional conversions when the required inputs exist. It does not predict conversion uplift or ROI. Permission status is a marketer declaration, not independent legal clearance.

## Code map

```text
marketer_app.py                 Local HTTP server and request validation
intrusive_ad_model.py           Privacy/pressure cue rules and OCR orchestration
ocr_ad.cjs                     Local English Tesseract.js runner
synthetic_simulation.py         Synthetic inference and level eligibility
stp_advisory.py                 A–E campaign and budget decision rules
threshold_engine.py            Empirical evidence gate and abstention
research_dashboard.py          Saved aggregate research views
web/                           Campaign, simulation and research interfaces
synthetic_demo/                Fictional data, generator and reproducible model
results/                       Versioned aggregate experiment outputs
test_*.py                      Regression tests
final_browser_checks.cjs       Real Chrome demonstration checks
```

The app serves `/`, `/simulation` and `/research`. JSON interfaces are `POST /api/analyze`, `GET /api/research`, and `GET` / `POST /api/simulation`. Image validation enforces supported types and size limits before OCR.

## Verification

The latest cue-repair regression run completed **128 tests: 127 passed, one skipped**. The completed application also passed **21 real Chrome workflow checks**. All **604 protected research artifacts** matched their recorded hashes during completion verification. These are recorded local results, not a claim that every environment has been tested.

```powershell
python -m unittest discover -q
python phase9_research/preservation.py verify
```

On the inspected Windows machine, Application Control blocks the native SPSS reader. The documented test-only R adapter reads the same SAV through installed R and `foreign`, without changing security policy:

```powershell
$env:PYTHONPATH = 'phase12_validation/compat;.phase8_vendor'
& 'C:\ProgramData\anaconda3\python.exe' -m unittest discover -q
```

The optional Phase 12 source-archive audit skips when `PHASE12_AD_CSV` and `PHASE12_AD_ZIP` are unset. Those variables must reference the original licensed local source files to enable that check. Browser checks additionally need Playwright, Chrome and the locally held test advertisement. The checked-in browser script uses the inspected Windows paths and port 8774; adjust them for another machine.

## Research, data and limitations

The project uses secondary research and explicitly fictional demonstration data. Real sources are analyzed separately; unrelated respondents are never joined to fabricate consumer histories. Local source files, restricted respondent exports, OCR scratch files and caches remain excluded from Git where documented. Dataset and model licenses are source-specific; repository availability does not replace those terms.

OCR can omit or corrupt text and requires human review. Cue rules recognize selected wording and can miss paraphrases. Correcting a transcript improves the text supplied for review, not automatic OCR accuracy. The application does not independently recognize image objects, verify targeting permissions, identify real customer segments or establish an individual's personalization threshold.

For implementation details and recorded checks, see the [final project report](49C_FINAL_PROJECT_REPORT.md). For empirical measurement compatibility and error analysis, see the [model validation report](PHASE5_MODEL_VALIDATION_REPORT.md), [linked-condition analysis](CORE_DATASET_RESOLUTION_AND_MODEL_RESULTS.md), and [data/model feasibility audit](STP_DATA_MODEL_FEASIBILITY_AUDIT.md). Historical reports preserve their original scope and dates.
