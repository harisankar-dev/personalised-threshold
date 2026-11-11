# English OCR and privacy repair results

## Dataset gate and evaluation

[HierText v1.0](https://github.com/google-research-datasets/hiertext) passed the gate. Its official repository provides actual Open Images JPG archives, complete word/line polygons and text, legibility and print/handwriting fields, official train/validation/test splits, and CC BY-SA 4.0 terms. The official 577,088,394-byte validation archive and 12,274,736-byte validation annotation were accessible. Annotation SHA-256: `ce7085d8bf24c2f13df852715c34494e6748cafcabb4bfc7a6e2bb320f58d23a`; archive MD5: `6a055aff4c749e43fcfbe9027d017904`.

Twenty-four visually inspected advertising-relevant validation images were frozen before OCR: 12 development and 12 untouched test images. They cover promotional signs, retail displays, print ads, web/email creatives, small print, text over photographs and multiple text regions. Exact hashes and 48 official line annotations are in `repair_validation/hiertext_reference_v1.json`. All image hashes are unique; the closest cross-set perceptual-hash distance is 18. CER/WER use 24 complete official line crops per split. Full-image phrase recovery tests the same 24 labelled lines per split. This bounded design avoids treating ambiguous multi-column page order as transcription error.

| Production Tesseract.js 7.0.0 | Development | Fresh test |
| --- | ---: | ---: |
| Images / complete line crops | 12 / 24 | 12 / 24 |
| CER | 0.4951 | 0.1927 |
| WER | 0.9157 | 0.4472 |
| Exact labelled phrases recovered from full images | 8/24 | 8/24 |
| Character / word insertions | 180 / 51 | 44 / 16 |
| Empty crops / empty full images / failures | 3 / 0 / 0 | 0 / 0 / 0 |
| Median line / full-image time | 0.359 s / 1.335 s | 0.335 s / 1.354 s |

These results establish a reproducible English baseline and confirm substantial remaining error. They do not support unattended OCR. Aggregate results are in `repair_validation/tesseract_metrics_v1.json`; raw OCR stays ignored locally.

## One local alternative

An isolated Python 3.13 environment was created because the project runtimes are Python 3.14/3.15. Official Apache-2.0 packages PaddlePaddle 3.2.0 and PaddleOCR 3.7.0 were installed; the Windows CPython 3.13 CPU wheel is available from the official package. PaddleOCR did not reach inference: Windows Application Control blocked the native `pandas._libs.indexing` extension during import. The policy was not bypassed, the Anaconda research environment was not changed, and no second engine was attempted. Paddle CER, WER, recovery and latency are therefore **unavailable**. Fresh-test OCR improvement is **not demonstrated**, so the production Tesseract path was not replaced or modified. The failed 1.0 GB environment and 1.2 GB of completed/partial archive-transfer files were removed after verification; the selected images and official annotations remain local.

## Privacy repair

`intrusive_ad_model.py` received a narrow text-rule correction:

- `We know where you live` → `precise_location`, high tier, 6/10.
- `We know what you searched for` → `browsing_history`.
- `We've tracked/monitored/followed your activity` → `explicit_surveillance`.

Targeted tests retain ordinary seller/form language, negation and meta-quotation handling. `Our address is…`, seller email, `Visit our store`, and `Enter your phone number to register` do not become viewer-identity claims. `We do not know where you live`, quoted bad examples and “for example, do not say…” remain unflagged. The known location example is development evidence. No independent reusable set of real privacy-positive ads was available, so real-ad privacy recall remains unmeasured and the synthetic cases establish software behaviour only.

## Functional verification

Ten installed-Chrome checks passed against the local app: a real English print ad, a real deadline success, a difficult retail deadline OCR miss retained as `needs_review`, viewer-location and tracked-activity claims, seller email, ordinary registration wording, unreadable-image abstention, unknown-permission hold, and affordable revision/headroom arithmetic. The difficult Milk-Bone image still misses its visible `limited time only` phrase, demonstrating the remaining OCR risk. No-cue images are not presented as safe.

The documented Phase 12 environment passed **114 tests with 0 failures, 0 errors and 0 skips**. All **604 protected files** matched their hashes. The threshold still returns `status: insufficient_evidence` and `recommended_level: None`. The exploratory 0–10 score remains an editorial cue rubric, not a consumer-discomfort prediction.

Files changed or added: `.gitignore`, `intrusive_ad_model.py`, `test_english_ocr_privacy_repair.py`, this report, and `repair_validation/{prepare_hiertext_subset.py,hiertext_reference_v1.json,evaluate_tesseract.py,tesseract_metrics_v1.json,browser_checks.cjs}`. Downloaded images, archives, raw OCR, browser results, the isolated environment and model/cache files are excluded from Git.

Remaining limits: Tesseract recovers only one-third of selected full-image phrases on both splits; complex development layouts have particularly high error; PaddleOCR is incompatible with the enforced Windows policy in this environment; OCR confidence is not calibrated; and independent real-ad privacy precision/recall is still unknown. Human review remains required.
