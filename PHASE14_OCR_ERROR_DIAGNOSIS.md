# Phase 14 OCR error diagnosis

**Scope.** English text extraction from ad images, not consumer-perceived intrusiveness. Starting implementation: commit `139de17a3b8e83fdc688fb2f52a31e587cdcc3b8`. Local engine: Tesseract.js 7.0.0, English traineddata SHA-256 `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`, Node 24.22.1; preprocessing uses Pillow 12.3.0 on Python 3.14.6. No image leaves the local machine during OCR.

## Observed mechanism

Phase 13 appended every second-pass line whose punctuation-stripped characters were not identical to a first-pass line. It could therefore append a near-duplicate (`WHITE: RIDAY.` / `WHITE ERIDAY,`), fragmented words, and unrelated background symbols. Its overall confidence number did not identify which *lines* were correct. Reading order became original-pass lines followed by transformed-pass lines, even when both referred to the same region. The extra material directly raises insertion operations in CER/WER. A full 1903 Gold Dust image also yields decorative-border symbols before its body copy, illustrating that full-image output can be much noisier than a bounded text region.

| Development diagnostic | Original pass | Phase 13 append policy | Phase 14 selection |
| --- | ---: | ---: | ---: |
| Salem 540 bounded English headline CER / WER | 0.6000 / 1.0000 | 1.3333 / 2.0000 | 0.6000 / 1.0000 |
| Gold Dust complete body-region CER / WER | 0.0075 / 0.0784 | 0.0075 / 0.0784 | 0.0075 / 0.0784 |
| Exact phrases across these two full images | 2/3 | 2/3 | 2/3 |

The historical Phase 13 six-image reserved set had 4/18 original-pass phrases versus 6/18 append-policy phrases, but two complete headline crops worsened from CER 0.2381 to 0.6032 and WER 0.6364 to 1.0000. That prior reserved set is development evidence now; it is not a fresh Phase 14 test.

## Decision

`intrusive_ad_model.py` now selects one transcript. It uses the original pass whenever that pass contains a Latin word of at least three letters. Only an original pass with no such word receives the existing bounded grayscale/contrast PSM 11 rescue. The rescue is displayed only with at least four Latin words and confidence at least 60; it carries a review warning. This is a conservative software policy, not confidence calibration or proof that words are correct. A long, very-low-confidence first transcript retains the severe-garble abstention. No line-level or automatic region selector was promoted because the development images do not establish reliable alignment or region detection.

Known residuals: small stylized headings still fail (Salem 540); seller/product text can be fragmented; mixed Arabic/English ads are outside English-only OCR coverage; full-image body copy may include decorative symbols; reading order can be wrong within one Tesseract pass; and a high-confidence OCR error can still trigger a cue. An image with no cue is sent to review rather than treated as comfortable.

Reproduction: `python -m phase14_validation.evaluate development baseline`, then `development phase13` and `development revised`, after obtaining source images at the hashes in the [frozen reference](phase14_validation/frozen_reference_v1.json). Detailed OCR strings remain in ignored `phase14_validation/local_results/`, avoiding redistribution of source copy.
