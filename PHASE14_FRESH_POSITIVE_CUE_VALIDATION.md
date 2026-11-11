# Phase 14 fresh positive-cue validation

## Labels and scope

One AI assistant visually checked two development and two reserved real images before the revised OCR test. Labels in `phase14_validation/frozen_reference_v1.json` refer to **observable wording**, not measured consumer discomfort. Gold Dust and Altair each assert a limited-time offer. Salem 540 and 532 have no assessable English deadline or identity claim in the bounded annotated content. The real YP Threads email excerpt reported by Ragtrader is a separate **text-only** privacy diagnostic. There is no independently annotated modern privacy-positive image in this set.

| Evaluation stage and cue | Assessable cases | Positive prevalence | TP / FP / FN / TN | Precision / recall / F1 |
| --- | ---: | ---: | --- | --- |
| Fresh test, text-rule deadline on visually checked phrase | 2 | 1/2 | 1 / 0 / 0 / 1 | 1 / 1 / 1 |
| Fresh test, full-image OCR → deadline rule | 2 | 1/2 | 1 / 0 / 0 / 1 | 1 / 1 / 1 |
| Fresh test, direct viewer identifier in images | 2 | 0/2 | 0 / 0 / 0 / 2 | undefined / undefined / undefined |
| Fresh test, explicit surveillance in images | 2 | 0/2 | 0 / 0 / 0 / 2 | undefined / undefined / undefined |
| Separate real email excerpt, text-rule surveillance | 1 | 1/1 | 0 / 0 / 1 / 0 | undefined / 0 / undefined |

The `1/1` image deadline recall is compatible with a true success probability as low as 0.025 under an exact 95% binomial interval. No broad performance claim follows from one positive. The real email wording (“We know where you live. Time starts now.”) currently yields `low_intrusive` 0/10 because the `explicit_surveillance` rule does not match it. That is a **false-reassurance risk** in the text workflow. It was discovered only after the final rule freeze; no post-test pattern was fitted to it. Phase 15 should use independent real examples and broader paraphrase/negation evaluation before repairing the rule. The phrase could also require campaign-context review; the article is not an independent coding panel.

Image-stage diagnosis: Altair's headline is read, its `limited time only` phrase is recognized, and the full pipeline returns `moderate_intrusive`, score 2/10, with a revise-one-creative advisory. This reflects an editorial pressure cue weight, not consumer intrusiveness. Salem 532's English product label is partly read, has a partial-OCR warning, and the image without matched cues returns `needs_review`, avoiding a low-risk conclusion. No real privacy-positive **image** was available, so privacy-image recall is unmeasured. Seller phone/email and negated/quoted wording were exercised in Chrome and synthetic regression, not counted as real cue positives.
