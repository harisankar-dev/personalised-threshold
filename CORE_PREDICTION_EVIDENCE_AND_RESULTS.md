# Core prediction evidence gate — 49-C

**11 November 2026 | Decision: NO-GO for a new personalization-dependent discomfort predictor.** This review used existing secondary-data audits and one bounded public-source search. It did not collect participants, download respondent records, fit a model, or change the application. The repository was clean at `2e0a9b83646a97e22e8c8cefc1e8c19ac65d81a0` before this report.

## Evidence inventory

| Source | Measured respondent-level information | Rights and fit for the core target |
| --- | --- | --- |
| [Romano–Han](https://data.mendeley.com/datasets/zcp5httw5c/1), 837 respondents | Six general unsolicited-social-ad intrusion items (1–7), privacy concern, perceived benefits, avoidance, demographics | CC BY 4.0; no assigned ad, personalization condition, or specific exposure. Existing V1/V2 models are same-survey research only. |
| [Gen Z personalized-ad survey](https://data.mendeley.com/datasets/czgx8b793m/1), 296 respondents | Perceived personalization, relevance and privacy worry | CC BY 4.0; no direct intrusion response or assigned condition. Supports descriptive privacy/relevance profiles, separately from Romano–Han. |
| [Redondo–Aznar](https://data.mendeley.com/datasets/89nk3kp8tg/1), 1,511 respondents | General web-ad interruption on a −3 to +3 scale | CC0 1.0; no assigned personalization; construct and scale differ from Romano–Han. |
| Vietnam privacy/trust survey, 467 respondents | Privacy practices, online trust, purchase intention | No advertising exposure or direct ad intrusion. |
| [Criteo Uplift](https://huggingface.co/datasets/criteo/criteo-uplift) | Binary ad treatment, visit/conversion | CC BY-NC-SA 4.0; no perceived intrusion, relevance or five-level condition. |
| UPAD | Recorded user–ad action types | No direct intrusion or reliable exposure-level denominator; the prior action predictor did not beat its constant baseline. |
| [Verenkotte–Spann OSF](https://osf.io/zv8xy/), 409 and 401 respondents | Two 2×2 experiments: location-targeting specificity × information-use disclosure, direct post-exposure privacy intrusiveness (`PPI`), relevance (`PPR`), perceived personalization (`PP`), click intention (`ITC`) | Best measurement match. The latest documented source review found no explicit dataset license or permission for the proposed retained modelling, and original exports include IP addresses, coordinates and participant IDs. No raw workbook was retained or modelled. Study 3 has four aggregate ad-set rows, not individual responses. See [rights review](PHASE9_DATA_RIGHTS_AND_PRIVACY_REPORT.md) and [intake decision](PHASE10_DATA_ELIGIBILITY_AND_PRIVACY_REPORT.md). |

No respondent linkage exists across these sources. Privacy concern is not an intrusion outcome; click intention is not observed click behaviour. The OSF experiments compare specific location/disclosure manipulations, not the project's L0–L4 methods.

## Bounded new-source check

Searches of OSF, Mendeley Data, Harvard Dataverse, Zenodo and original publication/repository pages sought respondent-linked personalization conditions and discomfort outcomes. The strongest newly identified leads were:

| Publication/repository | Verification and decision |
| --- | --- |
| [Penha, *AI-based Personalization in Advertising and Its Influence on Consumer Attitudes*](https://run.unl.pt/entities/publication/45928f60-313a-41a9-a1ea-c13d513b118c/full) | A 302-valid-response three-scenario experiment reports 1–5 intrusiveness, trust and engagement. Its repository lists a CC BY 4.0 thesis PDF and `license.txt`, but no respondent-level data file. Published group statistics cannot form an individual training set. The thesis reports 322 collected and 302 valid responses; its age description also conflicts with its stated adult-only exclusion, warranting a data audit if records become available. |
| [Zhang et al., *Too Sensitive, Too Much?*](https://research.wur.nl/en/publications/too-sensitive-too-much-triggers-and-consequences-of-perceived-sur/) | A 1,256-person sensitivity × data-amount experiment measures perceived **surveillance**, a related but different outcome. The checked institutional record supplies article details, not a verified licensed respondent table. No modelled source. |
| [Ansari et al., *Personalized Promotions and Perceived Intrusiveness*](https://zenodo.org/records/22249483) | The Zenodo file listing contains one article DOCX, not respondent data; no assigned treatment is established. |
| [Kim–Ha personalization-backfire experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC12561546/) | Three message conditions × privacy prime and purchase intention, but no direct intrusiveness target. Respondent data are on request; previous audit excluded it. |

The search did not verify any **new** source with all of: legally usable respondent records, an actual personalization condition, a direct linked intrusion/discomfort response, and enough observations for an untouched holdout. Public article access and CC licensing of a *thesis* do not establish access to an unlisted respondent table. This is a bounded search result, not proof that no suitable dataset exists anywhere.

## What existing results actually support

- **Individual discomfort:** **Limited.** The Romano–Han V1 ridge model predicted the same survey's *general-ad* 1–7 intrusion rating with held-out MAE **0.521** versus training-mean **0.815** (167 people). V2 MAE was **0.509**, but its gain over V1 had paired 95% interval **[−0.003, 0.028]**. For observed ratings ≥5, V2 predicted below 5 for **25/126**, versus **18/126** for V1. Contemporaneous privacy items share content with the target and are unavailable as known pre-exposure traits in the marketer app. Neither model predicts a person's reaction to a specified personalization method. See [V1](SECONDARY_SURVEY_PHASE_V1.md), [V2](SURVEY_PHASE_V2_REPORT.md), and [reliability audit](PHASE5_MODEL_VALIDATION_REPORT.md).
- **Consumer segmentation:** **Limited.** Existing [Phase 7 profiles](PHASE7_SEGMENTATION_EVIDENCE.md) describe privacy × relevance in Gen Z and privacy × perceived ad benefits in Romano–Han, with source-specific counts and bootstrap intervals. They are survey descriptions, not stable, targetable customer identities or consent signals. No new cluster fit was justified by the evidence gate.
- **Personalization-level recommendation:** **Unsupported.** No eligible data measure a direct discomfort outcome across the proposed L0–L4 levels for the same decision setting. Existing `threshold_engine.py` correctly returns `insufficient_evidence`; no level was imputed or recommended.

## Engineering disposition

**No application, threshold, dataset, model, or test files changed.** No model fitting, train/test split, leakage evaluation or Chrome test was applicable because no new capability passed the evidence gate. The only addition is this source-and-decision report. The targeted `python -m unittest test_threshold_engine` run passed **5/5** tests; the full regression suite was not rerun for a documentation-only change. The existing model metrics above are quoted from saved reports, not re-estimated here.

The next concrete unlock is a source-specific reuse grant or explicit data license **and** a privacy-reviewed, identifier-minimized respondent release for the OSF location experiment (or an equivalent licensed experiment). That would permit a narrow study-specific condition model, subject to an untouched holdout and high-intrusion false-reassurance audit. It still would not establish all five levels or justify deployment to arbitrary marketer ads.
