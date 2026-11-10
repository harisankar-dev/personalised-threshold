# Phase 12 — real-image OCR reliability audit

**Method:** ten versioned JPG IDs from [Salem et al. v1](https://data.mendeley.com/datasets/32grwbk6rv/1) were checked against their archive SHA-256 bytes, passed unchanged through `ocr_ad.cjs` with the local English Tesseract model, and screened with the unchanged cue rubric. Exact per-image dimensions, publisher `text` field, local OCR strings, OCR confidence and downstream cues are recorded in `phase12_validation/ocr_observations_v1.json`. The publisher's semi-automatically extracted `text` is a useful comparison, **not** an independently verified character-by-character transcript. Accordingly no character-error rate, word-error rate or OCR accuracy percentage is claimed. OCR confidence is the engine's internal value, not a calibrated probability of cue correctness.

| Image ID | Pixels | Observed condition | OCR / downstream result |
| --- | ---: | --- | --- |
| 403 | 736 × 1308 | Tall fashion ad; thin top letters, huge textured “SALE”, fine time-limit text | Returned only `SO eOrr` (confidence 1). The visible/publisher “limited time only” was lost; image prediction abstains `needs_review`, no score. |
| 484 | 526 × 526 | Angled product layout with rotated and large words | Recovered fragments including `LIMITED` and `TIMES` (confidence 60), but not a faithful phrase; no pressure cue, `needs_review`. The unchanged text rule also misses the publisher's “limited time offer”. |
| 389 | 736 × 736 | Text over photo, lower-edge seller phone | OCR returned a seller contact number; the rubric misread it as the viewer's `direct_identifier`, giving **high, 6/10** on this image. This is a referent error, with OCR supplying a contact absent from publisher text. |
| 379 | 512 × 640 | Dark recruitment design, small contact email | OCR recovered internship wording but mangled the email (confidence 41). Source-text screening falsely flags the employer email; image OCR happened not to flag it. |
| 451 | 512 × 640 | Stylized Halloween lettering around objects | OCR missed most of the figurative “before they vanish” phrase (confidence 43); scarcity is already ambiguous in the codebook. |
| 12 | 526 × 443 | Small Arabic-English phone offer with Arabic stock notice | English OCR mostly gibberish (confidence 20); no Arabic reading capability. |
| 400, 469, 474, 498 | 512–736 px wide | Product imagery, mixed typography or Arabic text | Partial and noisy English extraction; no matched cue in these four. This does not verify absence of cues in unread text. |

Local OCR confidence among these ten ranged from **1 to 60**. This is a deliberately chosen small observational slice, with no random sampling or verified transcription. It cannot estimate population OCR error or language-specific performance. The image IDs, conditions and output are reproducible by `python -m phase12_validation.audit_ocr` using local publisher files and extracted, hash-matching JPGs.

## Stage attribution

1. **OCR:** the visible text can be omitted or corrupted by scale, orientation, stylized glyphs, text over photographs, dense product copy and Arabic script. ID 403 shows severe text loss.
2. **Cue matching on publisher-extracted text:** IDs 403 and 484 still miss time-limited urgency even when the publisher text contains it; this is a rule-coverage error separate from OCR.
3. **End-to-end image result:** IDs 403 and 484 abstain on no matched cues rather than falsely claiming low risk. ID 389 gives a false high-risk identifier finding because the screen cannot tell advertiser contact data from a viewer identifier.

No image object recognition, visual obstruction assessment, emotional-imagery interpretation, actual tracking detection, campaign-targeting inference or consumer response prediction is supported. A zero-cue OCR output is **not** evidence of a low-intrusion ad. OCR reliability work needs verified human transcriptions, broader formats and language-specific readers before any performance claim or promotion to an automated decision.
