# Phase 13 fresh real-ad evaluation

## Source and separation

The images came from [Salem et al., Advertising Images Dataset for Visual Analysis, Mendeley Data v1](https://data.mendeley.com/datasets/32grwbk6rv/1), whose listing states CC BY 4.0. Downloaded inventory: 605 JPGs and 605 CSV rows, despite a 606-record page description. Social-platform creative rights have not been independently established; original images and full OCR dumps stay outside Git. The source is mostly Arabic and has no consumer intrusiveness labels, actual personalization treatment, permission, targeting exposure or engagement outcome.

The [pre-run reference](phase13_validation/real_ad_reference_v1.json) fixed image IDs, short English visible phrases, condition notes, two cue categories and split before final scoring. One AI-assisted project reviewer visually checked it against source images; it is not independent human ground truth. Development IDs: **420, 431, 472, 483, 495, 516**. Reserved test IDs: **450, 500, 503, 510, 517, 538**. All 12 differ from Phase 12's 25 annotated IDs. Exact SHA-256 and 64-bit difference-hash distance ≤5 checks found no duplicate or near-duplicate among the 37 compared images. This does not rule out all semantic or campaign-template similarity in the full 605-image archive. IDs 483 and 503 were marked unassessable for English cue absence because Arabic content is adjacent.

No labels were derived from the detector. The publisher CSV OCR was not used as transcription truth. All 12 have only partial English phrase references; three bounded headline crops have complete references for region-specific CER/WER. There are no real viewer-specific identity or deadline positives in this split, despite deliberate source search. This restricts performance claims. The final six were scored once after the initial rule freeze. A later **code-review** fix narrowed generic “enter your phone number” wording, without using these ads to select the change. A second regression run of the same six showed identical phrases and cue outputs, and refreshed timing measurements. This set is no longer untouched evidence for a future phase.

## Separate evaluations

**1. Text cue detection.** Using the project-checked visible English phrases on five assessable test images and the two predeclared cues (`direct_identifier`, `urgent_call_to_action`) gives 10 cue opportunities. Phase 12 baseline: TP 0, FP 1, FN 0, TN 9. Revised: TP 0, FP 0, FN 0, TN 10. The sole baseline false alarm is seller email on ID 538. No positive instances exist, so recall, precision and F1 are undefined. These conditional counts cannot validate general cue detection; incomplete phrase references can hide other cues.

**2. OCR.** Exact full-image phrase recovery increased from **4/18 to 6/18** on the reserved six images and **4/15 to 7/15** on development six. Neither version returned an empty transcript or process failure. Median per-image test time increased **0.466→1.008 seconds** (max **0.806→1.489 seconds**) on the post-review rerun. Five of six revised test images received a partial-OCR warning. On two predeclared complete English headline crops (500, 517), micro CER **0.2381→0.6032** and WER **0.6364→1.0000**, a clear degradation caused in part by added text/noise. These metrics are crop-specific. No deadline-positive real ad was available to measure deadline OCR recovery. [OCR report](PHASE13_ENGLISH_OCR_VALIDATION.md) gives cases and limits.

**3. End-to-end image screening.** Across the same 10 assessable cue opportunities, baseline TP 0, FP 1, FN 0, TN 9; revised TP 0, FP 0, FN 0, TN 10. On ID 538, OCR recovered a public seller email and the revised classifier correctly avoided a viewer-identity cue. No real positive was available to distinguish OCR loss from a missed cue rule. Images without detected cues returned `needs_review`, so no low-risk image reassurance was issued. An image can still receive a false high cue from OCR; this small sample does not bound that rate.

| ID | Test condition | Baseline / revised exact phrases | Main finding |
| ---: | --- | ---: | --- |
| 450 | Tiny rotated shoe lettering | 0/1 · 0/1 | Both miss |
| 500 | Script and price over photo | 1/4 · 1/4 | Headline partly read; crop error worsens |
| 503 | Mixed Arabic and English | 0/3 · 1/3 | English price recovered; cue absence unassessable |
| 510 | Angled banners | 1/3 · 1/3 | “BUY 2 GET 2” recovered, other banners missed |
| 517 | Small top and vertical text | 0/2 · 0/2 | Both miss; crop error unchanged |
| 538 | Curved text and seller email | 2/5 · 3/5 | Email retained; old high privacy false alarm removed |

The original Phase 12 test remains a frozen diagnostic (two limited-time false negatives among 11 assessable English ads), not part of this fresh matrix. Phase 11 synthetic F1 0.923 is separate. None of these quantities measures consumer discomfort, calibrated intrusion, personalization threshold, conversion uplift or audience compatibility. A more representative, independently transcribed English source with genuine urgency and viewer-specific positives is the next validation gap.
