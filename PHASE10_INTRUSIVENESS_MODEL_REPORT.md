# Phase 10 — privacy-intrusiveness model decision

**Training status: no new model trained.** The closest individual-response source, [Verenkotte–Spann OSF `zv8xy`](https://osf.io/zv8xy/), has public files but no verified source-specific reuse and derivative rights for this workflow, and its original lab exports contain identifiers. The licensed alternatives in [the candidate matrix](phase9_research/candidate_matrix.csv) lack the joint assigned-personalization and direct ad-specific intrusion measurement. Phase 10 loaded **zero** OSF respondent rows, defined **zero** new train/test observations and fitted **zero** new models. Existing V1/V2/Criteo and other results were preserved, not rebranded as experimental validation.

## Narrow research question if the data gate opens

The target would be `PPI`: the respondent's post-exposure **perceived privacy intrusiveness** on the verified study scale for one assigned location-targeting/disclosure stimulus. It would not be a person's universal maximum tolerance or the marketer application's exploratory 0–10 creative score. Permitted pre-exposure predictors are `Targ`, `Trans`, their interaction and any independently verified pre-exposure covariates. Study 1 and Study 2 must be estimated separately because the low targeting arm differs. `PPR`, `PP`, `ITC`, post-exposure attitudes, IDs, IP addresses and coordinates are forbidden as pre-launch `PPI` predictors. A future model would be labelled **Research-only — location-targeting privacy-intrusiveness model** and would not be connected to `/api/analyze`.

## Prespecified evaluation ladder, not executed

1. Confirm rights, minimization, stimulus and composite scoring, missingness, duplicate handling and study-specific treatment coding. Record an immutable partition specification before opening outcome results.
2. Within each study, reserve one respondent-disjoint, treatment-cell-stratified holdout. The synthetic-tested partition helper keeps repeated observations together and rejects a respondent assigned across between-subject cells. Fit imputation, encoding and any scaling on training data only; cross-validate model choices inside training.
3. Compare a constant **training-mean `PPI`** predictor with an interpretable regularized condition model using `Targ`, `Trans` and their interaction. Add a third model only if genuine pre-exposure features have justified timing and coverage. Consider nonlinear modelling only for a prespecified scientific reason and enough observations. Do not tune on the final holdout.
4. Report holdout MAE plus RMSE against the constant baseline, respondent-bootstrap uncertainty intervals, treatment-cell MAE/counts, and high-intrusion **false reassurance** under a prespecified, scale-validated boundary. Report low-intrusion errors as well. If predictive intervals are offered, examine coverage overall and by cell, residual shape and calibration. Do not pick a high/low boundary after reading holdout errors.
5. Report source and stimulus transfer separately. Respondent-disjoint validation within one running-event creative family is **not** independent validation for arbitrary ad text/images, audiences or channels. Study 1 versus Study 2 changes the targeting contrast, so any cross-study check is bounded transport, not clean external validation.

| Requested result | Actual Phase 10 result |
| --- | --- |
| New fitted experimental model and saved artifact | None |
| Constant and condition baselines | Specified only; no fitted scores |
| Holdout MAE/RMSE and uncertainty | Unavailable; no holdout opened |
| High-intrusion false reassurance and low-intrusion error | Unavailable; no eligible predictions |
| Cell/subgroup performance and predictive-interval coverage | Unavailable |
| Generalization to user-uploaded ads | Unsupported |

The existing creative screen is a heuristic cue rubric, not a substitute ground truth for this experimental target. No measured five-level personalization threshold was constructed; `threshold_engine.py` continues to return `insufficient_evidence` on the current data.
