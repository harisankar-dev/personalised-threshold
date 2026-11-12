# 49-C · The Personalization Threshold

A local web application for reviewing advertisements, exploring fictional consumer profiles, and comparing personalization options against permissions and budgets.

## Features

- **Creative analysis:** flags selected privacy references, tracking claims, urgency and pressure tactics in ad copy.
- **English image OCR:** extracts printed text locally and lets you correct it before analysis.
- **Consumer simulation:** estimates simulated discomfort and relevance for fictional individuals and segments.
- **L0–L4 comparison:** compares generic, contextual, behavioral, historical and combined personalization.
- **Campaign planning:** checks declared permissions, implementation costs, budget headroom and break-even additional conversions.
- **Research dashboard:** presents separate findings from secondary research datasets with source attribution.

**Scope:** this is an academic demonstration. Consumer simulations use generated data and are labelled **Synthetic data**. The creative score is an editorial screening rubric. Neither is a validated prediction of a real person's response.

## Install and run

You need Python, Node.js/npm, and a modern browser. The application was tested with Python 3.14.6 and Node.js 24 on Windows. Other environments have not been verified.

```powershell
git clone https://github.com/harisankar-dev/personalised-threshold.git
cd personalised-threshold

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-research.txt
npm install

python marketer_app.py
```

Open **http://127.0.0.1:8765/** if the browser does not open automatically. Keep the terminal running; press **Ctrl+C** to stop the server.

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead of the Windows activation command above. These platforms have not been tested.

To use a different port:

```powershell
python marketer_app.py --no-browser --port 8774
```

Then open **http://127.0.0.1:8774/**.

Image OCR requires `models/eng.traineddata` and the npm dependency `tesseract.js`. The application uses local OCR and does not require paid APIs, API keys or a cloud account. The large historical Criteo archive uses Git LFS; it is not required to run the demonstration.

## Try the application

1. In **Campaign planner**, paste one advertisement or upload a PNG, JPEG, WebP, BMP or TIFF image under 10 MB. Paste only the creative, rather than a document containing several examples.
2. Select **Analyze ad**. Review the matched cues and editorial screening score. For images, open the OCR section, edit the transcript if necessary and select **Analyze corrected text**.
3. Enter known campaign details, permissions and costs. Review the A–E options and budget calculations. Leave unknown figures blank.
4. Open **Consumer & levels**. Select a fictional profile or segment, set acceptable simulated discomfort and relevance, confirm available data permissions, and enter incremental costs.
5. Select **Compare L0–L4**. The app shows simulated outcomes, eligibility reasons and a demonstration recommendation—or abstains when the criteria cannot be met.
6. Open **Research evidence** to inspect actual source-specific findings separately from the simulation.

Campaign form values persist within the browser session, and campaign budget headroom is shared with the simulation. Images must be reselected after navigating away.

Example ad copy:

```text
We know you searched for running shoes last night, bought a pair six months
ago, and usually run near Miramar Beach. Your new shoes are waiting!
```

This should expose browsing, purchase-history, location and combined-data cues. It is a fictional software example, not consumer-response evidence.

## Personalization levels

| Level | Approach | Required data in the demonstration |
| --- | --- | --- |
| L0 | Generic | No individually tailored targeting |
| L1 | Contextual or broad demographic | Context or broad demographic data |
| L2 | Behavioral | Browsing, search or interaction history |
| L3 | Historical | Purchase or customer relationship history |
| L4 | Combined / hyper-personalized | Context, behavior and history together |

A level is eligible only when its data permissions and financial inputs meet the stated checks. Unknown permission triggers review. Missing costs or headroom prevent a financial feasibility claim. The simulation selects the simplest eligible level meeting the user's discomfort and relevance criteria. It does not automatically apply that choice to a real campaign.

## Read the results correctly

| Result | Meaning |
| --- | --- |
| Creative score, 0–10 | Rule-based screening points for observable privacy and pressure cues. |
| Synthetic discomfort/relevance, 1–7 | Simulated outcomes learned from fictional consumer data or averaged within fictional segments. |
| Real survey profiles | Descriptive groups from separate research samples, not identified advertising audiences. |
| Budget and break-even figures | Arithmetic based on entered costs and margins; no predicted ROI or uplift. |
| `insufficient_evidence` | The real-data engine has insufficient evidence for a validated individual L0–L4 threshold. |

The synthetic model uses quadratic features and Ridge regression. Its 60-consumer synthetic holdout achieved discomfort MAE **0.512**, compared with **0.765** for a level-mean baseline. This measures fit to generated assumptions, not accuracy on real consumers. OCR and cue screening still require human review.

## Troubleshooting

- **Missing Python package:** confirm the virtual environment is active, then rerun `python -m pip install -r requirements-research.txt`.
- **OCR dependency error:** run `npm install` from the repository root and confirm `node --version` works.
- **Missing English language data:** confirm `models/eng.traineddata` exists. See [OCR/model documentation](MODEL_README.md).
- **Port already in use:** choose another port with `--port` and open the matching URL.
- **A level is ineligible:** inspect its explanation. Confirm the required data and permitted use, provide costs and headroom, and check the response criteria.
- **OCR missed text:** edit the extracted transcript and analyze the correction. The application does not independently recognize visual objects.

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

## Development and tests

The saved synthetic model is included; retraining is optional. To reproduce it:

```powershell
python -m pip install scikit-learn==1.9.0
python synthetic_demo/train.py
```

Run the application regression suite from the repository root:

```powershell
python -m unittest discover -q
```

The cleaned distribution passes **71 application tests with no failures or skips**, verified in an isolated copy containing only the retained files. These cover creative cues, input validation, empirical abstention, STP budgets/permissions, synthetic simulation and segmentation.

The full development workspace previously ran 128 tests (127 passing, one optional research-source audit skipped) and 21 real Chrome workflow checks. Historical research tests, local browser fixtures and machine-specific test scripts are excluded from this application-focused distribution.

## Research and data use

Real and synthetic records are kept separate. Source-specific licenses and restrictions still apply to research datasets; repository access does not grant additional reuse rights. The application does not independently verify permission, identify actual customer segments, predict conversions or validate an individual's personalization threshold.

For further details, see the [completion report](49C_FINAL_PROJECT_REPORT.md), [research validation](PHASE5_MODEL_VALIDATION_REPORT.md), and [synthetic-data documentation](synthetic_demo/README.txt).
