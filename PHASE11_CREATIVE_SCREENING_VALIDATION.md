# Phase 11 — creative-screening validation

**Scope, 9 November 2026:** This is a software and heuristic cue audit. It does not estimate consumer-perceived intrusion or the accuracy of the three tiers against people. The 0–10 number is a capped editorial cue total, not a probability or a calibrated rating.

## Exact implemented rubric

The versioned [regex inventory](phase11_validation/rubric_inventory_v1.json) exports **every exact pattern, source, weight, derived rule, threshold and cap** from `intrusive_ad_model.py`. The script `python -m phase11_validation.rubric_inventory` recreates it. Each cue contributes at most once; when the same cue occurs in ad copy and targeting text, the higher-weight instance wins. A generic `personalized_claim` is removed when a concrete browsing, purchase or location cue is present. The new local denial guard skips an explicitly denied phrase and inspects later matches in the same text. It is syntactic, not general language understanding.

| Source and cue | Points | What the exact patterns seek |
| --- | ---: | --- |
| Ad copy: direct identifier; sensitive personal fact; explicit surveillance | 6; 6; 5 | Email/phone formats; directly addressed diagnosis, debt, pregnancy and similar facts; explicit tracking/watching or knowing activity. |
| Ad copy: precise location; approximate location | 6; 2 | Home/address/current whereabouts versus broad nearby or named-city availability tied to the reader. |
| Ad copy: browsing history; purchase history; interest targeting; personalization claim | 3; 3; 2; 1 | Observed searches/visits; orders/cart; explicit known interest; generic tailored/recommended wording. |
| Targeting text: sensitive fact; browsing; purchase; precise location; approximate location; broad targeting | 6; 3; 3; 6; 2; 1 | Declared data-use terms such as `purchase history`, `GPS`, `current city`, `age:`; a denied use is now scoped out. |
| Pressure: countdown; scarcity; extreme discount; urgent call; alarmist claim | 3; 2; 2; 2; 2 | Timer/digital clock; `limited stock` or `only N left`; 80–100% off; `last chance`/`act now`; alarm or takedown claims. |
| Derived: combined personal signals; activity detail; no consent; repeated exclamations | 1; 1; 2; 1 | Two distinct personal signal categories; browsing plus timing detail; explicit lack-of-permission language; at least two runs of `!!!`. |

Raw privacy and pressure points are separately returned and summed. The displayed score is `min(10, raw sum)`. Low is below 2, moderate is 2–5, high is 6 or more raw points. Empty input needs review. An image with no matched text cues also needs review; a blank OCR image has no score. Local English OCR reads printed words, not image objects, visual aggression, page obstruction or targeting actually used. OCR confidence is reported as an OCR property, not a calibrated confidence in the intrusion tier. Repair actions are editorial suggestions mapped to matched cues; they have no measured consumer effect.

## Evaluation provenance and annotation protocol

The frozen [26-case set](phase11_validation/creative_cases_v1.json) has SHA-256 `08a2428ee34598314311383189e35b4cc437715c889e158deca07c0044041676`. It was saved and evaluated **before** changing the rubric. Its expectations are author-defined semantic **software diagnostics**, with explicit positives, negated uses, quotes, mixed clauses and implicit phrasing. An explicit cue asserts use or pressure in the ad; a denial or instruction not to say/use it does not. A real offer quoted as the ad's headline still counts. Conditional promises, sarcasm, reassurance and tracking disclosure remain context-dependent and require human review. No consumer ratings or independent human cue annotations were invented.

The existing six StrideFit conditions in `survey_sanity_cases.json` are separate fictional tier sanity checks from the supplied document, not independent consumer labels. The local [CHI ad-perceptions dataset README](secondary_data/chi-bad-ads-data/README.md) describes 500 ad screenshots and opinion/content labels, but its available labels do not match this exact cue taxonomy and no applicable reuse license was established in the local copy. It was **not** relabelled as privacy-cue ground truth or used for a precision claim. The supplied aggressive screenshot was tested in the real browser as an OCR functional case, not added as a consumer-rated observation.

## Diagnostic results on the same frozen cases

The [baseline output](phase11_validation/creative_baseline_v1.json) and [after output](phase11_validation/creative_after_v1.json) are reproducible with `python -m phase11_validation.evaluate_creative`. Multi-label cue counts use one case–cue occurrence as the unit; neither the 26 cases nor their cue expectations are a representative sample.

| Author-defined fixture result | Before | After local denial fix |
| --- | ---: | ---: |
| True-positive cue occurrences | 18 | 18 |
| False-positive cue occurrences | 7 | 1 |
| False-negative cue occurrences | 2 | 2 |
| Micro precision | 0.720 | 0.947 |
| Micro recall | 0.900 | 0.900 |
| Micro F1 | 0.800 | 0.923 |

The six removed false positives were a denied surveillance quote, an instruction not to use an urgent phrase, two denied targeting data sources, and a mixed declaration where the denied purchase source previously created a false combined-signal cue. The remaining false positive is rhetorical scarcity later retracted (`Only 3 left? No.`). The two remaining false negatives are a pregnancy paraphrase and an implicit browsing reference. Those errors reflect semantic scope and expression coverage; adding a phrase for each fixture would overstate generality. No weights or thresholds changed. The source file contains the exact confusion counts by cue and case type; several categories have only one positive, so per-category F1 is especially unstable.

**Independent ad cue performance:** not measured. **Consumer intrusion prediction accuracy:** not measurable from these fixtures. The next defensible evaluation is a permission-cleared, independently annotated collection of diverse real ad copy/images with a written cue codebook, separate annotators and disagreement review; consumer-rated intrusion would be a further, distinct validation task.
