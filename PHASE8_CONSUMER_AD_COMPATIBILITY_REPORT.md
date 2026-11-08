# Phase 8 — consumer–advertisement compatibility and model boundary

**49-C | 8 November 2026 | Secondary data only.** The product question is: given a specific creative and a declared campaign configuration, which audience approach could be relevant without unjustified discomfort or additional cost? The current system can organize the evidence and ask for the right checks. It cannot estimate a customer's or survey profile's response to an uploaded ad.

## 1. Operational definition

Consumer–ad compatibility would require a **defined exposure** to a creative, under a known targeting/data-use condition, for an eligible consumer, followed by **separate** measurements of perceived relevance, perceived intrusiveness and engagement. A useful comparison must consider the same product/category and channel, audience reach and incremental cost. A low privacy concern answer is neither consent nor evidence of comfort with every tracking method. Positive copy sentiment is neither relevance nor low intrusion. Purchase intention, click intention, observed click and conversion are distinct outcomes. This report assigns **no numerical compatibility score**, since the required target and independent validation are absent.

| Dimension | Available in 49-C now | Evidence type and interpretation | Missing for a validated compatibility prediction |
|---|---|---|---|
| Creative wording and printed image text | Uploaded text, local English OCR, optional marketer visual description | **Observed/marketer-supplied** text; rule-matched privacy/pressure cues and capped 0–10 **heuristic** points | Validated image-object/layout understanding and direct ratings of this creative |
| Category, channel, method and data source | Structured Phase 8 marketer inputs; existing objective, permission and eligibility declarations | **Declared, unverified** context; source/method consistency is a review rule | Verified platform configuration, provenance and lawful eligibility |
| Consumer relevance/usefulness and privacy concern | Separate Gen Z and Romano–Han survey scales | **Direct questionnaire measures within those survey samples**, aggregate research profiles | A legitimate bridge to this campaign audience and its ad exposures |
| Intrusiveness and response | Romano–Han/Redondo general-ad ratings; OSF location experiment `PPI`, `PPR`, `ITC`; OSF field ad-set clicks | Direct **general-ad** and **specific-stimulus** survey outcomes, plus separate aggregate field behaviour | Licensed/minimized linked observations for this uploaded ad and eligible audience, actual click/conversion denominator |
| Business contribution | Marketer-entered budget, committed spend, cost, margin and scenarios | **Deterministic arithmetic** and explicitly hypothetical incremental-conversion scenarios | Credible causal uplift and reach/expense estimates under the selected option |

The [OSF location-targeting replication project](https://osf.io/zv8xy/) is an important new lead: its 409-row Study 1 and 401-row Study 2 each contain randomized targeting/disclosure conditions, direct relevance and privacy-intrusiveness composites, and click intention in the same respondent record. Study 3 has four aggregate ad-set rows with observed clicks and impressions. The repository has **no explicit data license** and its raw lab exports contain IP addresses, coordinates and participant IDs. Phase 8 inspected schemas/aggregate counts in memory but kept no raw workbook or fitted artifact. The [Kim–Ha backfire study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12561546/) offers a relevant 3×2 treatment/purchase-intention result, but row-level data are available only upon request and it does not directly measure perceived ad intrusion. Full source and quality findings are in `PHASE8_SECONDARY_EVIDENCE_SEARCH.md`.

## 2. What the new compatibility code actually does

`phase8_compatibility.assess()` returns a separate `compatibility` object when an `/api/analyze` request includes `campaign`. The old API without `campaign` is unchanged. The assessment labels creative cues as a heuristic screen, campaign values as marketer declarations, survey profiles as unrelated aggregate descriptions and financial scenarios as user hypotheses. It lists matched privacy/pressure cue classes, detects declared source/method conflicts and missing permission/eligibility for personal sources, and gives a concrete pre-launch measurement plan. It sets `compatibility_score`, consumer relevance prediction, consumer intrusion prediction, segment assignment and expected extra conversions to **`null`**. It explicitly reports the five-level threshold as `insufficient_evidence`.

`stp_advisory.py` now also asks for review when a declared source conflicts with the method, when a personal method has an unspecified source, or when third-party/other data use cannot be checked. Verified-looking form values are **self-declarations**; the system does not issue legal clearance. This gate affects the action (`hold_for_review`) but never invents a marketing response. The original five budget options A–E remain visible, with A the no-extra-cost comparator. C–E still are **not automatically recommended**. The browser adds product category, channel and data-source selectors, and a plain-language evidence panel beside the Phase 7 advisory. No customer file is requested in default Mode A.

### Evidence labels and readiness

| Output or component | Phase 8 label | Permitted use |
|---|---|---|
| OCR/copy cue tier and 0–10 rubric | Heuristic screen, operational prototype | Human creative review; **not** a calibrated consumer rating |
| Declared method/source and permission checks | Conservative workflow rule | Spot inconsistencies and pause for verification; **not** legal compliance proof |
| Gen Z / Romano–Han profiles | Separate descriptive survey evidence | Explain that benefit/relevance and privacy concern can coexist; **not** actual company segments |
| A–E budget option table and break-even | Validated formula on supplied numbers | Compare known costs and hypothetical scenarios; **not** forecast uplift |
| Consumer–ad compatibility score or segment targeting | Unsupported | Abstain |
| Five-level personalization threshold | Unsupported | Remain `insufficient_evidence` |

## 3. Model decision

**No new supervised model was trained in Phase 8.** The most relevant candidate has directly measured specific-stimulus outcomes, but no explicit reuse license, direct identifiers in the published workbook, only one running-event creative family, lab click intention rather than individual observed clicks, no verified marketing permission and no five-level treatment design. A trained predictor with post-exposure `PPR`/`ITC` used as pre-launch features would leak outcomes. A model without them could test a narrow condition-response question only after reuse rights and data minimization are resolved. It would remain research-only until respondent/ad-disjoint holdout performance, high-intrusion false-reassurance, subgroup uncertainty and external transfer are measured. Current Romano/Redondo V1–V3, Criteo and UPAD artifacts remain separate and unchanged; their saved metrics are not compared as if they estimate the same target.

## 4. What remains unsupported

- Predicting whether a specific company customer would like or fear this uploaded ad.
- Mapping survey profile membership onto audience records, or excluding a person based on privacy concern.
- Sentiment, product-object recognition, true visual obstruction and ad-category extraction from images.
- Claiming a positive hypothetical scenario justifies more variants or audience fragmentation.
- Predicting a validated 0–10 discomfort score, engagement lift or an optimal level 0–4 personalization threshold.

The next evidence-backed step is a **licensed, minimized, linked experiment** with creative and treatment identifiers, pre-exposure audience features and permitted data use, direct intrusion and relevance ratings, and engagement on the same exposures. A narrow location-specific study could be evaluated first; it cannot be relabelled as the complete five-level threshold or attached to unrelated marketer uploads.
