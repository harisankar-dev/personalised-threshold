# Phase 14 English OCR accuracy

## Reference and protocol

The [frozen reference](phase14_validation/frozen_reference_v1.json) fixes two development and two fresh test creatives, source SHA-256 hashes, region boxes, complete bounded English-region transcripts, exact phrase probes and cues. One AI assistant visually transcribed the visible regions before running revised OCR. There was no independent human double annotation. References were not copied from either OCR output or the publisher's automatic transcript. Bounded-region CER/WER use lowercase alphanumeric text with punctuation collapsed to spaces. They do **not** represent full-ad CER/WER. Exact phrase recovery probes the full-image transcript. The two Salem images are mixed-language ads, but the measured regions are English.

Source images stay outside Git. Original-pass OCR, frozen Phase 13 OCR and revised OCR were run on the same four source hashes. The Phase 14 implementation was fixed before the two test images were evaluated. The test split was evaluated once for method selection; no later cue or OCR rule was tuned to its results. The [aggregate metrics](phase14_validation/metrics_v1.json) and [evaluation script](phase14_validation/evaluate.py) are versioned. The local raw transcripts are ignored.

| Split and OCR method | Creatives | Region micro CER | Region micro WER | Exact full-image phrases | Median full-image seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development, original pass | 2 | 0.0393 | 0.1132 | 2/3 | 0.722 |
| Development, Phase 13 append | 2 | 0.0786 | 0.1509 | 2/3 | 1.030 |
| Development, Phase 14 select | 2 | 0.0393 | 0.1132 | 2/3 | 0.812 |
| Fresh test, original pass | 2 | 0.0514 | 0.1087 | 4/6 | 2.180 |
| Fresh test, Phase 13 append | 2 | 0.0514 | 0.1087 | 4/6 | 2.407 |
| Fresh test, Phase 14 select | 2 | 0.0514 | 0.1087 | 4/6 | 2.040 |

The fresh test **does not show an OCR accuracy improvement** over the original pass or Phase 13: both test regions gave identical transcripts/metrics across methods. Phase 14 recovers the original-pass accuracy on the development failure case and avoids a second OCR process when the first has English words. Timing differences are descriptive for two heterogeneous images, not a robust speed estimate; the 2448×3261 Altair scan took over three seconds. No phrase-recall gain was observed on this split. The failed exact phrases include small or punctuation-sensitive words; phrase counts are not a substitute for CER/WER.

At the image stage, the real Altair headline's `limited time only` is legible in the full OCR output and the product-label Salem 532 image yields `Balsamic Vinegar` and `Sea Salt`; the latter image has a low-confidence warning and returns review when no cue is found. On the development Salem 540 ad, `SMASHING PRICES` was not recovered by any method. The original Gold Dust body region was transcribed accurately despite noisy full-image border extraction. These are four creatives, one annotation pass, two sources and historical ad layouts: no general English-ad OCR reliability estimate or uncertainty interval is defensible. The next validation requires independent transcripts on a larger, diverse, licensed English set.
