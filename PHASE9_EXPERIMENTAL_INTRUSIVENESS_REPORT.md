# Phase 9 — experimental intrusiveness modelling decision

**49-C | 8 November 2026 | Status: evidence gate closed; no Phase 9 model trained.** This is an executed eligibility and design review, not a report of numerical model performance. The original survey, UPAD and Criteo experiments remain separate; no existing result was overwritten.

## Candidate observation and construct map

The [Verenkotte–Spann article](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216) and [OSF replication tree](https://osf.io/zv8xy/) describe the closest available experiment. Phase 8 inspected **409 Study 1** and **401 Study 2** respondent rows in memory, with no saved raw copy; their core condition/composite fields had no missing values in that inspection. Study 1 randomized **no versus high/city location targeting** × **no disclosure versus information-use disclosure**. Study 2 randomized **low/country versus high/city location targeting** × the same disclosure contrast. Both are between-subject experiments. Study 3 is **four ad-set aggregate rows** with observed impressions and clicks; it is neither 4 respondents nor a linked consumer-level validation sample. The pooled Study 1/2 workbook repeats those experiments and is not an independent third cohort. These are not 49-C's five personalization levels.

| Variable | Meaning and timing | Permitted role in a pre-launch intrusion model |
|---|---|---|
| `Targ`, `Trans` | Assigned location specificity and disclosure conditions | Candidate predictors after study-specific codebook verification. The same `Targ` code has a different low arm in Study 1 and Study 2. |
| `PPI` and its items | Respondent-rated **privacy intrusiveness after this stimulus** | Preferred separate target, subject to item direction/scale checks and reuse rights. It is not a general tolerance ceiling. |
| `PPR` and its items | Respondent-rated personal relevance after exposure | A separate outcome for a separate analysis, **not** an input to predict `PPI` before launch. |
| `PP` | Perceived personalization after exposure | A separate manipulation/response measure, **not** a pre-launch input shortcut. |
| `ITC` | Click **intention** after exposure | A separate response outcome, **not** an observed click or conversion and not an input to predict `PPI`. |
| Study 3 ad-set counts | Aggregate actual impressions, clicks and spend | Descriptive field comparison only; cannot be merged onto Study 1/2 respondents. |
| Pre-exposure respondent features | Only those explicitly timed before stimulus | Potential covariates after codebook verification and missingness review; demographic categories alone do not establish consumer preference or consent. |

Privacy concern before exposure differs from the ad-specific `PPI` response. The marketer app's OCR/copy **0–10 rubric** is neither this target nor a calibrated transformation of it. `PPR`, `PP`, `ITC`, post-exposure attitudes, participant IDs, IP addresses and coordinates are barred as pre-launch `PPI` predictors. A composite of relevance, intrusion and clicking would erase the research question and was not created.

## Why fitting stopped

The OSF node currently reports a **null dataset license**, and its [README](https://osf.io/download/tw6dm/) gives only replication instructions. The available original workbooks include IP addresses, precise location and participant identifiers. No explicit reusable, identifier-minimized release was located. The [rights/privacy report](PHASE9_DATA_RIGHTS_AND_PRIVACY_REPORT.md) documents the checks and an unsent permission request. The licensed alternatives lack the required direct intrusion × assigned personalization exposure linkage. Consequently, **0 Phase 9 training rows were loaded, 0 holdout rows were defined, 0 models were fitted, and 0 evaluation metrics or uncertainty intervals were generated**. No fabricated estimate stands in for these missing results.

## Predeclared narrow protocol if the gate opens later

This protocol is prospective, **not performed**. It must be revised against the granted codebook and minimized release before any fitting.

1. Record the actual written grant/license, attribution, derivative and retention terms. Reject files containing raw IP, precise coordinates, direct platform IDs or unneeded free text. Validate study provenance, stimulus version, response scale, treatment coding, missing values and one-row-per-respondent assumption. If repeated exposures exist, require a stable pseudonymous group key and keep all of a person's rows in one partition. Treat duplicated answer vectors without IDs cautiously; they are not proof of duplicated people.
2. Define Study 1 and Study 2 **separately**. Do not pool their `Targ` codes without explicit recoding: Study 1 compares no/city; Study 2 compares country/city. Study 3 remains aggregate. Set `PPI` as the directly rated outcome; analyze `PPR` and `ITC` as separate responses. Record all feature definitions before seeing a test score.
3. Reserve a single respondent-disjoint, treatment-cell-stratified holdout per study before selecting models. Use training-only imputation/scaling and cross-validation on the training partition. The constant **training-mean `PPI`** is Baseline 1. A regularized condition-only model with `Targ`, `Trans` and their interaction is Baseline 2. Add only justified, verified **pre-exposure** covariates for an interpretable third model. A nonlinear candidate requires a predeclared reason and training-only selection. Never tune on the final holdout.
4. Report holdout MAE and a second scale-aware error summary versus the constant baseline, bootstrap respondent-level intervals, cell sizes and errors by targeting/disclosure condition, and high-intrusion **false reassurance** under a threshold specified from the validated scale before inspecting the holdout. Also report low-intrusion subgroup error and uncertainty. Do not call a model calibrated merely because average error is small; inspect residuals and, if intervals are supplied, empirical interval coverage.
5. Check whether stimulus-disjoint validation is possible. With the currently described running-event stimulus family it likely is **not**; respondent-disjoint performance would not show transfer to new products, image styles or an arbitrary marketer upload. A Study 1→Study 2 comparison changes both targeting contrast and possibly stimulus/population, so it is a bounded transport check, not a clean external replication. Account for sample-size limits in each 2×2 cell.
6. Promote any acceptable fit only to **research-only: location-targeting privacy-intrusiveness response**. Do not send it into `/api/analyze`, infer company customer comfort, automatically select segments, claim conversion uplift, or recommend one of the five 49-C personalization levels.

## Results and uncertainty actually available in Phase 9

| Requested output | Phase 9 result |
|---|---|
| Licensed/minimized individual-level training source | **None verified**. |
| Model, predictors, holdout and constant baseline | **Not fitted/evaluated** because the intake gate failed. |
| Holdout MAE, uncertainty interval, subgroup error and false reassurance | **Unavailable; no holdout was opened**. |
| Study 1/2 condition effects and relevance–intrusion coexistence from our own analysis | **Not re-estimated**. The publisher's qualitative findings are discussed separately in the STP report and are not 49-C model metrics. |
| Independent creative-family validation | **Unavailable**. |

The current five-level threshold remains `insufficient_evidence`. A two-factor location experiment, even if licensed later, cannot be relabelled as generic/contextual/behavioural/historical/combined treatments or used to interpolate missing levels.
