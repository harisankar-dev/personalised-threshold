# Phase 7 — exploratory customer preference profiles

**7 November 2026. Secondary data only.** Reproduce with `PYTHONPATH=.vendor python phase7_segmentation.py --output <new-path>`; the default versioned result is `results/phase7_segmentation_v1.json` and refuses overwrite. The script pins SHA-256 source hashes, checks shape/item order and response bounds, and writes **aggregate counts only**. Its groups are transparent descriptions of survey answers, **not** trained clusters, individual preference predictions, consent indicators, or targetable campaign audiences.

## Sources, variable mapping and decision

| Source | Rows, response scale and fields used | Why it helps | What it cannot establish |
|---|---|---|---|
| [Gen Z personalized-advertising survey](https://data.mendeley.com/datasets/czgx8b793m/1), `try these dataset/GenZ_Personalized_Ads_Purchase_Dataset_N296.xlsx` | 296 rows; publisher verifies 1=strongly disagree to 5=strongly agree. Relevance is mean of original columns 17–21; privacy concern is mean of columns 26–29 (zero-based). Full Turkish item headers are in `STP_DATA_MODEL_FEASIBILITY_AUDIT.md`. | Same respondents report both personalized-ad relevance and privacy worry. | No direct intrusion rating, assigned personalization method, ad-specific exposure, consent or observed conversion. 18 birth years from 2009 onward conflict with the publisher's adult-sample description at 2026; cohort inference is uncertain. |
| [Romano–Han unsolicited-social-ad survey](https://data.mendeley.com/datasets/zcp5httw5c/1), `try these dataset/Consumer perceptions towards unsolicited ads on social media.sav` | 837 rows; 1–7 agreement scale in prior item audit. Perceived ad benefits = mean `PAB1–PAB4`; privacy concern = mean `PC1–PC6`. | Same respondents report benefits and privacy concern; separate `I1–I6` direct general-ad intrusion exists for research. | Benefits refer to unsolicited ads generally, not personalized-ad relevance. No uploaded creative, treatment, click or operational audience ID. SAV lacks embedded question/value labels; meaning depends on the published descriptor and prior item audit. |

Both datasets have 0 missing scale-item cells. One Gen Z and two Romano answer vectors are exact duplicates; no respondent IDs exist, so these were retained and are not asserted to be the same people. Neither source was merged with the other, UPAD or Criteo. The publisher records show CC BY 4.0. Sampling is not representative of a marketer's campaign audience. Low privacy concern **never** implies legal consent.

## Predeclared descriptive rule

For each respondent, calculate a simple average for each axis. On Gen Z's 1–5 scale, **higher** means average ≥3.5, between neutral 3 and agree 4; on Romano's 1–7 scale, **higher** means average ≥4.5, between neutral 4 and agree 5. The four labels are combinations of higher/lower reported value and concern. No fit, optimization or outcome-based threshold tuning was performed. The axis names are source-specific: **relevance** for Gen Z, **perceived ad benefits** for Romano.

| Source and profile | Respondents | Share | Within-source respondent-bootstrap 95% share interval |
|---|---:|---:|---:|
| Gen Z: higher relevance, lower privacy concern | 33 | 11.1% | 7.8–14.9% |
| Gen Z: higher relevance, higher privacy concern | 88 | 29.7% | 24.7–34.8% |
| Gen Z: lower relevance, lower privacy concern | 82 | 27.7% | 23.0–32.8% |
| Gen Z: lower relevance, higher privacy concern | 93 | 31.4% | 26.0–36.8% |
| Romano: higher benefits, lower privacy concern | 110 | 13.1% | 10.9–15.5% |
| Romano: higher benefits, higher privacy concern | 500 | 59.7% | 56.4–63.1% |
| Romano: lower benefits, lower privacy concern | 46 | 5.5% | 4.1–7.1% |
| Romano: lower benefits, higher privacy concern | 181 | 21.6% | 18.8–24.5% |

Intervals use 2,000 seeded respondent resamples **within each source**; they describe row-sampling variation, not population representativeness or profile-transfer accuracy. Percentages may differ by 0.1 point due to rounding. The Romano high-benefit/high-concern cell is large; concern and benefit are not opposites. Gen Z relevance and privacy concern have Spearman ρ **0.1772**; Romano benefits and privacy concern ρ **0.1599**. These are separate survey constructs, not evidence for a treatment preference. For comparison, the existing Gen Z audit's perceived-personalization/privacy association ρ **0.2088** uses a *different* first axis.

## Reliability and stability

| Check | Gen Z | Romano–Han | Interpretation |
|---|---:|---:|---|
| Cronbach alpha, value axis | 0.8712 | 0.9482 | Internal consistency of item group, not validity of a targetable segment. |
| Cronbach alpha, privacy axis | 0.8723 | 0.9211 | Same limit. |
| Leave-one-item-out assignment agreement | 90.9–97.0% | 95.0–97.4% | Most assignments survive removing one item, but some lie near cutoffs. |
| Agreement when both cutoffs shift −0.25 | 88.5% | 94.4% | Threshold choice changes composition. |
| Agreement when both cutoffs shift +0.25 | 88.5% | 88.2% | Threshold choice changes composition. |

For example, Romano's higher-benefit/higher-concern cell changes from **500** at the primary cutoffs to **436** at +0.25. These are *rule sensitivity* diagnostics; no temporal retest or independent survey replication exists. Item wording and response style may induce overlap, especially between same-wave attitudes. Gen Z's birth-year metadata inconsistency and Romano's lack of respondent IDs limit claims. The segment names are descriptive hypotheses; they should not be translated into “personalization comfortable,” “tracking averse,” expected conversion, exclusion or targeting rules.

## Why no cluster model was added

The two-axis, midpoint-based rule already communicates the available evidence without choosing a distance metric, cluster count or validation target on a small, survey-only source. Clustering would not create ad exposure, consent, a link to an actual audience or segment-level uplift. There is no ground-truth class and no operational deployment variable against which to judge cluster utility. A later clustering study would need prespecified features, sample-size/stability checks, construct validation and an independent outcome source. This phase deliberately leaves the two datasets separate and presents only aggregate exploratory profiles in the marketer app.
