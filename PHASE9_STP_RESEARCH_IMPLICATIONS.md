# Phase 9 — bounded STP research implications

**49-C | 8 November 2026.** These are literature-grounded research implications, not new 49-C treatment-effect estimates or instructions to launch a campaign. No respondent-level Phase 9 experiment was analyzed because reuse and privacy conditions remain unresolved.

## What the external evidence says

The [Verenkotte–Spann publication](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216) reports that more specific **location** targeting can raise perceived personalization and engagement, while consumers weigh personal relevance and perceived privacy intrusiveness together. It describes a context-dependent disclosure pattern: transparency can ease privacy-related disengagement for less specific targeting, but can draw attention to personal-data use under highly specific targeting. Those are the authors' study-specific conclusions across two lab experiments and a separate field experiment, **not independently reproduced Phase 9 effects**. The lab measured click **intention**; field clicks were reported in aggregate ad sets, not linked to lab respondents. The location and running-event context limits transfer to other products, channels, creatives and data types.

Existing 49-C local evidence is narrower in different ways. The [Gen Z survey](https://data.mendeley.com/datasets/czgx8b793m/1) measures perceived personalized-ad relevance and privacy worry in the same respondents, but no assigned ad condition or direct ad-intrusion rating. The [Romano–Han survey](https://data.mendeley.com/datasets/zcp5httw5c/1) measures benefits, concern and general unsolicited-ad intrusion, but no rated uploaded ad. Their descriptive profiles show that perceived value and concern can coexist; they are **not company audience segments**. [Criteo](https://huggingface.co/datasets/criteo/criteo-uplift) has a binary ad treatment and behavior but no privacy/relevance response or creative. No cross-source consumer records were linked.

## Decisions the current product may support

**Segmentation:** Use the two existing survey profiles as separate aggregate research descriptions. They can motivate questions for a future study, such as whether relevant copy and disclosure affect different respondents differently. They cannot identify or exclude an actual customer, estimate segment uplift or imply consent. A preference survey and a marketing eligibility record are different evidence.

**Targeting:** The Mode A form can flag a declared source/method mismatch, unknown permission or eligibility, and sensitive data use for review. A highly specific location tactic merits a direct response and permission check, but the external study does not certify a campaign's legal eligibility or optimal setting. Do not infer that the most precise targeting is always best, or that disclosure has one universal effect.

**Positioning:** Revise visible pressure/privacy wording in **one creative** when the heuristic screen identifies cues, and test the revised copy with appropriate exposure-level outcomes. The current 0–10 score is an editorial cue rubric, not consumer-rated intrusion. The OSF publication cannot tell whether an arbitrary image upload will feel intrusive.

**Budget:** Keep the existing A–E comparison: **A** keep the campaign, **B** revise one creative, **C** adjust eligible targeting within the same campaign, **D** test one additional variant, and **E** consider multiple variants only with credible incremental value. The existing calculator correctly compares user-entered costs, headroom and hypothetical break-even conversions; it does **not** forecast actual uplift. No publication result or positive what-if arithmetic authorizes C–E. A costly extra segment needs an eligible reachable audience, a measured incremental outcome and an uncertainty-aware net-value comparison against A.

## Unsupported claims and next evidence step

Phase 9 did not establish a new consumer intrusion model, a calibrated 0–10 consumer discomfort number, customer-level relevance, permission, click-through lift, actual conversion gain or a five-level threshold. Mode A remains a working research-informed advisory **prototype**. Mode B remains an **offline schema design**; no real customer-file upload or audience inference was enabled. `threshold_engine.py` still returns `insufficient_evidence` for levels 0–4.

The next defensible step is the [unsent permission request](PHASE9_OSF_DATA_PERMISSION_REQUEST.md). If the authors permit a minimized release and derivative model, implement the prospective, study-specific protocol in [the experimental report](PHASE9_EXPERIMENTAL_INTRUSIVENESS_REPORT.md). A separate, licensed stimulus-diverse validation set would then be needed before any advice about unrelated uploaded ads. A campaign decision additionally requires lawful audience data, an actual impression denominator, direct relevance/intrusion responses and observed outcomes under a budgeted comparison.
