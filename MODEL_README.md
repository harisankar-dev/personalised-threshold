# 49C three-tier ad screen

This screen estimates **ad-content intrusiveness risk** from two explicit components: personal-data cues and high-pressure marketing tactics. It does not assess whether an ad disrupts a webpage, obscures content, or violates Better Ads Standards. That is a different problem studied by [Adhere](https://ieeexplore.ieee.org/document/10172610).

This creative screen is separate from the consumer-level **Personalization Threshold** decision contract. `threshold_engine.py` returns `insufficient_evidence` on the current secondary data because the required per-level outcomes and direct intrusion ratings are absent. The local interface displays that status instead of presenting a personalized recommendation. See `UPGRADE_V0_1_0.md` for the evidence and release plan.

## Algorithm

`intrusive_ad_model.py` is a **rule-based, three-class proxy classifier**. It extracts English text from an image with Tesseract.js OCR, combines it with any supplied ad copy, visual description, and optional targeting settings, then looks for privacy and pressure cues. Approximate location scores 2; browsing or purchase history scores 3; explicit surveillance scores 5; direct identifiers, sensitive personal facts, and precise location score 6. Countdown pressure scores 3; scarcity, extreme discounts, urgent commands, and alarmist claims score 2 each; repeated exclamation runs add 1. A cue family contributes once even when repeated. Combining two distinct personal-data sources adds 1, and specific activity details or lack of consent can add further points. The response reports separate privacy and pressure cue totals. The displayed **0–10 score is their sum capped at 10**. Scores 0–1 are low, 2–5 moderate, and 6–10 high. The 0–10 number is not a probability or measured consumer response.

This is not K-means clustering. The 60 supplied ads have no consumer-rated intrusion labels and do not span three verified intrusion groups. K-means would force a third group even if all ads were similarly generic. This proxy gives the requested three outputs without calling arbitrary clusters observed intrusiveness. **Do not report accuracy or confidence probabilities:** none can be estimated from these files.

## Use

From this folder, run either:

```text
python intrusive_ad_model.py --text "Shop our new fall collection"
python intrusive_ad_model.py --text "Your cart is waiting" --targeting "purchase history"
python intrusive_ad_model.py --image path/to/ad.png
python marketer_app.py
```

`marketer_app.py` starts a local browser interface at `http://127.0.0.1:8765/`. It accepts pasted copy or a drag-and-drop image, optional targeting details, and an optional description of non-text imagery. It shows the tier, 0–10 score, both cue totals, matched evidence, editing suggestions, and text read from an image. The suggestion workflow adapts Adhere's detect-explain-repair idea to ad content; these edits have not been tested with consumers. The server binds only to the local computer. Image support needs Node.js, `tesseract.js`, and `models/eng.traineddata`; the English OCR data came from the [official Tesseract tessdata_fast repository](https://github.com/tesseract-ocr/tessdata_fast/blob/main/eng.traineddata). On this workspace, the bundled `tesseract.js` dependency and local language file are present. For a new machine, install `tesseract.js` with npm and place the English traineddata file in `models/`.

OCR reads text inside an image. It does not identify visual objects, faces, page obstruction, or layout. An image with no matched cues now returns `needs_review` rather than a reassuring low score, even if OCR found generic wording. Low on text means **no matched cue**, not proof that consumers will feel comfortable. The supplied aggressive Instagram-style image returns **high, 10/10** from its countdown, scarcity, extreme-discount, urgent-command, and alarmist text. Its privacy cue total is 0; the pressure cue total is 12 before the display cap.

An independent diagnostic sample from the [University of Washington Ad Perceptions Dataset](https://github.com/eric-zeng/chi-bad-ads-data) exposed the rule screen's limited coverage. Before image abstention, 29 of 30 sampled ads with high participant shares for clickbait, deceptive, or manipulative labels were called low by the rubric. After the change, those 29 receive `needs_review`; one remains high. The same fixed sample's 30 low-concern ads also receive `needs_review`. These opinion labels are **not** direct intrusiveness ratings, so these counts show coverage and abstention behavior, not classification accuracy or improved discrimination. See `results/external_creative_audit_before_abstention.json` and `results/external_creative_audit.json`.

## Data limitations

The original 49-C CSVs provide ad copy and recorded action types, but not human intrusion ratings, personalization treatments, or a reliable exposure denominator. The class labels are rubric-defined screening tiers. The existing event model in `analysis.py` predicts click versus another recorded action and is unrelated to perceived intrusiveness. A separate 837-person secondary survey in `try these dataset/` does contain six direct general intrusiveness ratings; its independent respondent-level model is documented in `SECONDARY_SURVEY_PHASE_V1.md`. It has no rated ad creatives or five-level treatments, so it cannot validate this three-class creative screen or its 0–10 rubric. A learned and validated ad-level classifier still requires human intrusion ratings linked to actual ad content.

The six fictional StrideFit ads in `Personalized_Advertising_Intrusiveness_Survey.docx` were used as **sanity cases**, not respondent labels. The corrected scores are A 0, B 2, C 3, D 3, E 9, and F 10. The expected tiers and score ranges are recorded in `survey_sanity_cases.json` and checked by `test_model.py`. A–F progressing as designed demonstrates coverage of those examples; it does not estimate predictive accuracy. The survey document contains no completed ratings.
