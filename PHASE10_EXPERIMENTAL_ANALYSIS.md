# Phase 10 — experimental analysis and its evidence boundary

**No new respondent analysis or treatment-effect estimation was performed in Phase 10.** Reuse authorization for the closest OSF source remains unverified. The observations below come from the earlier, non-retained [Phase 8 schema and aggregate inspection](PHASE8_SECONDARY_EVIDENCE_SEARCH.md), not from a Phase 10 training file, open holdout or independent replication.

## What has been inspected previously

| Study | Unit and count | Treatment comparison | Prior 2×2 cell counts, ordered `(Targ, Trans)` = `(0,0), (0,1), (1,0), (1,1)` |
| --- | --- | --- | --- |
| Study 1 | 409 online respondents, 63 export columns | No location targeting versus city targeting × no disclosure versus information-use disclosure | 107, 98, 98, 106 |
| Study 2 | 401 online respondents, 108 export columns | Country targeting versus city targeting × the same disclosure contrast | 100, 100, 100, 101 |
| Study 3 | Four **aggregate ad-set** rows | Field ad-set conditions, impressions and clicks | Not respondents; no lab-row linkage |

The pooled Study 1/2 workbook repeats those respondents; it is not another 810-person validation set. Prior inspection found zero missing values in the six `Targ`, `Trans`, `PPI`, `PPR`, `PP`, `ITC` core fields; full exports had 1,637 and 9,625 missing cells, respectively, mostly in other fields. The earlier check found distinct `ResponseId` and `PROLIFIC_PID` counts matching each study's rows and no exact full-row duplicates. This does not certify all response validity, questionnaire timing or composite scale scoring. The original questionnaire wording, stimuli and item reversals require a fresh authorized source review before modelling.

## Previously observed descriptive ratings

These are the prior Phase 8 cell means on the source's reported 1–7 composites. They are **descriptive only**, not Phase 10 effect estimates or held-out predictions.

| Study/outcome | `0,0` | `0,1` | `1,0` | `1,1` |
| --- | ---: | ---: | ---: | ---: |
| Study 1 `PPI`, privacy intrusion | 2.561 | 3.542 | 3.241 | 4.028 |
| Study 1 `PPR`, personal relevance | 3.065 | 3.446 | 3.272 | 3.308 |
| Study 2 `PPI`, privacy intrusion | 2.413 | 3.088 | 3.107 | 3.595 |
| Study 2 `PPR`, personal relevance | 2.511 | 2.642 | 3.100 | 2.910 |

The means alone do not identify an interaction, reliable subgroup effect, individual-level relevance–intrusion covariance, or advertising benefit. In particular, `Targ=0` is a **different condition** in each study. Click intention (`ITC`) is not actual click-through rate. Study 3's ad-set clicks cannot be attached to lab respondents, and its four rows cannot validate an individual predictor.

The [published article](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216) discusses location-targeting specificity and disclosure effects. Its conclusions are the authors' findings; Phase 10 did not independently reproduce their effects. The experiment's running-event creative context and population limit transfer to other products or channels.

## Analysis preconditions and prospective method

Once use and privacy are authorized, first verify respondent and cell counts, exact stimulus assignment, randomized factors, questionnaire item wording, composite construction and missingness. Estimate each study **separately** with `PPI ~ Targ + Trans + Targ×Trans`, prespecifying the scale and uncertainty method. Repeat separately for `PPR`, `ITC` and `PP`; do not combine these into a synthetic target. Report cell means, study-specific effect contrasts, interaction estimates and respondent-level confidence intervals, with multiplicity and exploratory analyses labelled. Inspect whether individual relevance and intrusion can rise together without treating correlation as causal mediation. The randomized factors support condition comparisons within each experiment if assignment and validity are confirmed; post-exposure associations remain observational. No numerical Phase 10 effects, intervals or p-values exist because the eligibility gate is closed.

These location/disclosure factors are not the five 49-C levels. No five-level threshold, optimal targeting setting, customer segment, profit uplift or universal creative claim follows from the current descriptive table.
