# Phase 12 — frozen real-ad creative-text evaluation

**Evaluation tier B:** 25 publisher-described social ads from [Salem et al. v1](https://data.mendeley.com/datasets/32grwbk6rv/1), each interpreted once by the AI assistant from the publisher-extracted copy, with selected image spot checks. Source CSV and ZIP hashes, annotation definitions, IDs and splits are frozen in `phase12_validation/real_ad_labels_v1.json`; machine-readable outputs are in `phase12_validation/real_ad_baseline_v1.json`. No publisher visual-quality or human-preference label was reused as cue truth. These are **AI-assisted project-authored labels**, with no independent human cue annotator, adjudication panel or inter-rater statistic. **There are no consumer-perceived intrusion labels.**

The chosen set deliberately includes time-limit wording, discounts, product copy, an employer contact email, generic city delivery, ambiguous figurative scarcity and mixed Arabic-English creatives. It is a bounded stress sample, not a random probability sample. Exact image and extracted-text duplicates are absent among the 25; a coarse perceptual-hash check found no close pair at Hamming distance ≤5. Eight IDs were frozen as development and 17 as test before the current rubric was run. Six mixed-language test creatives were unassessable for this English-only binary estimate. One test scarcity cue was marked ambiguous and excluded from that cue denominator. No campaign targeting declaration accompanies these ads, so `broad_targeting` is not evaluated.

## Existing rubric, evaluated once without tuning

One creative–cue decision is the unit for the 18 assessable codebook cues. The 0–10 point weights and three tiers were **not** refitted. Negative cue cells are numerous; their count must not be presented as consumer-safety accuracy.

| Frozen partition | Creatives / assessable | Positive cue labels | TP | FP | FN | TN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Development | 8 / 8 | 0 | 0 | 1 | 0 | 143 | 0.000 (1 predicted positive) | Undefined (0 actual positives) | 0.000 diagnostic |
| Untouched test | 17 / 11 | 2 | 0 | 0 | 2 | 195 | **Undefined** (0 predictions) | **0/2 = 0.000** | 0.000 diagnostic |

The one excluded ambiguous scarcity instance accounts for 197 rather than 198 assessable test cue cells. A Wilson 95% interval for test recall of 0/2 is **0.000–0.6576**; it is extremely wide and does not justify a general recall estimate. Test precision has no denominator. Macro F1 across cues is not meaningful because almost every cue has zero positives; the only positive test cue class is `urgent_call_to_action` (0 TP, 2 FN, 9 TN). No privacy-positive ad exists in this slice, so privacy-cue recall and high-intrusiveness false reassurance cannot be estimated. Category-specific metrics are unavailable because the source has no verified per-ad category. Channel is only publisher-described social media, not per-ad platform. Arabic cases were excluded from English metrics rather than counted as correct negatives.

## Error inspection

- **Development false positive, ID 379:** the regex interprets the advertiser's public recruiting email as the viewer's `direct_identifier`. The codebook correctly requires an identifier *of the viewer*. This illustrates a referent/ownership problem, not a need to add one exception string.
- **Held-out false negatives, IDs 403 and 484:** both explicitly state a limited-time offer. The current urgent-call pattern lacks those common time-pressure phrasings. Their images also have OCR issues described separately.
- **Ambiguous ID 451:** “before they vanish” could refer to a Halloween theme or inventory; the scarcity cell is withheld from binary scoring.
- **Mixed-language IDs 12, 416, 463, 469, 476 and 505:** English-only extraction and this annotation pass cannot establish full creative cue absence.

No model or app rules were changed after inspecting final test outcomes. Therefore there is **no baseline-versus-improved real-ad claim** in Phase 12. Phase 11's 26 author-defined synthetic software fixtures still yield 18 TP, 1 FP and 2 FN (micro F1 0.923) and remain Tier A. Comparing that number to this small, single-annotator real-ad stress set as though they sampled the same distribution would be misleading. Tier C independent real-ad cue labels and direct consumer responses remain unavailable.

## Reproduction

Download both files from the linked source to a local location, verify the two SHA-256 hashes in the label JSON, then from the project root run:

```powershell
& 'C:\ProgramData\anaconda3\python.exe' -m phase12_validation.evaluate_real_ads --csv 'C:\path\to\Advertising Image Dataset for Visual Analysis.csv' --zip 'C:\path\to\ad_images.zip' --output 'C:\path\to\new_result.json'
```

The command refuses to overwrite an existing output. It checks the 605-ID inventory and selected exact duplicates, then scores only assessable, non-ambiguous cells. The project preserves the frozen result for future comparison without reusing the same test as a tuning set.
