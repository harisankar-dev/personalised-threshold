# Phase 13 English OCR validation

**11 November 2026. Scope:** local English printed-text extraction for a pre-launch creative review aid. The OCR output is neither a consumer response nor a calibrated confidence score. [Aggregate metrics](phase13_validation/metrics_v1.json) and reproducible scripts are versioned; downloaded JPGs and full OCR dumps remain local and ignored by Git.

## Source, references and split

The source is Salem et al., *Advertising Images Dataset for Visual Analysis*, [Mendeley Data v1](https://data.mendeley.com/datasets/32grwbk6rv/1), listed CC BY 4.0. The downloaded archive contains 605 JPGs, while the publisher page describes 606 records. Original social-platform creative redistribution rights are not independently verified, so the JPGs are not committed. Six development and six reserved test images were selected from unused IDs; none overlap the 25 Phase 12 annotated IDs. The sample deliberately includes small, angled, mixed-language and photograph-overlaid English text. It is convenience selected, predominantly from an Arabic collection, and cannot estimate general English-ad OCR accuracy.

The [frozen reference](phase13_validation/real_ad_reference_v1.json) records exact short phrases visible to one AI-assisted project reviewer, conditions and split. It was visually checked against the images before the final OCR run. No independent annotator or inter-rater agreement exists. Most references are partial; full-image CER/WER against them would be invalid. Three predeclared bounded headline regions have complete English references and support region-specific CER/WER only. Unclear or occluded wording was omitted. The publisher CSV's semi-automatic text was not treated as ground truth.

## Initial configuration and development work

The original `ocr_ad.cjs` used local Tesseract.js 7.0.0, `eng.traineddata` (4,113,088 bytes), default page segmentation, and no preprocessing. The app accepts PNG, JPEG, WebP, BMP and TIFF up to 10 MB. It sends files locally to Node; no cloud OCR. On the six development images, original OCR recovered 4/15 frozen phrases. Image 420 yielded pages of visual noise with low engine confidence; 431 missed the readable “ARGAN OIL” and “145 EGP”; 495 missed small white photographic text. Tesseract confidence was never interpreted as transcription accuracy.

On development images, we compared original, PSM 11 sparse text, 2× color, 2× grayscale, 2× grayscale/autocontrast/1.4× contrast, and 2× color PSM 6. These runs are reproducible with `python -m phase13_validation.ocr_experiment` when the licensed source archive is supplied locally. Results varied by typography. Enhanced PSM 11 recovered “ARGAN OIL” and “145 EGP” on 431 and more wording on 516, but it did not recover the angled small brand on 420 or the photographic headline on 495. A single transformation is not uniformly superior.

The application now takes the original pass first. If its engine confidence is at most 65 or it has fewer than four alphabetic words of at least three letters, it makes one extra local grayscale, autocontrast and 1.4× contrast pass with PSM 11. Image scaling is capped at 1600 pixels on the longest side, avoiding a very slow 2× pass on a 1536×2048 image. Distinct normalized lines from both passes are retained; the combined output is capped at 5,000 characters. A partial-extraction warning accompanies the second pass. Very long, low-confidence garbage causes `needs_review` with no numeric score when no other user-supplied text exists. Empty OCR also abstains. The app still does not assess visual objects or Arabic text.

## Before/after measurement

| Measure | Development, 6 images | Reserved test, 6 images |
| --- | ---: | ---: |
| Frozen phrases | 15 | 18 |
| Original exact phrase recovery | 4/15 | 4/18 |
| Revised exact phrase recovery | 7/15 | 6/18 |
| Original / revised empty outputs | 0 / 0 | 0 / 0 |
| Original / revised OCR failures | 0 / 0 | 0 / 0 |
| Original / revised median processing | 0.431 / 1.069 s | 0.466 / 1.008 s |
| Original / revised maximum processing | 3.750 / 5.186 s | 0.806 / 1.489 s |
| Revised partial/garbled warnings | 6/6, including one severe | 5/6, none severe |

On the two complete **reserved-test headline crops** (IDs 500 and 517), micro CER worsened from **0.2381 to 0.6032** and micro WER from **0.6364 to 1.0000**. On development crop 472, CER worsened from 0.5417 to 0.8750 and WER from 0.3333 to 0.8333. The extra pass introduces insertion noise; phrase recall alone must not be presented as general OCR improvement. CER/WER here are normalized edit distances on bounded regions, not full-image scores. Region cropping is used only for this metric, not by the live app.

There were **no genuine promotional deadlines in the six-image reserved test**, so real-ad deadline OCR recovery is unmeasured. A generated, high-contrast English deadline image containing “LIMITED TIME OFFER” was uploaded in Chrome and correctly extracted and cued. That is a software integration check, not independent real-ad validation. The Phase 12 missed deadline images are now diagnostic and were not promoted to a fresh holdout.

## Browser and remaining limitations

Real Chrome uploads passed for a clear English headline (516), a generated deadline, small text (517), text over a photograph (500), angled promotion (510), seller phone (389), seller email (538), blank and poor-quality generated images, and a mixed-language ad (483). All image cases displayed OCR text or a review state; blank and difficult images were not silently scored low. See [browser results aggregate](phase13_validation/metrics_v1.json) and [browser script](phase13_validation/browser_checks.cjs).

**Readiness: conditional review aid.** Ordinary clear headlines can be extracted, but stylized, angled, low-contrast and mixed-language text remains unreliable. The dual-pass transcript can be noisier, even while recovering more selected phrases. The current evidence does **not** establish dependable general English OCR or deadline recall in real ads. Phase 14 should evaluate line-level selection or text-region detection using a larger independently transcribed, reuse-cleared English set with real deadline positives before changing this policy again.
