# Phase 12 — product validation and readiness

**10 November 2026.** Mode A remains a working, explainable, local **pre-launch STP advisory prototype**. Phase 12 adds a small, real-ad **Tier B** creative-text stress evaluation and a separate observational image/OCR audit. It does **not** validate a consumer intrusiveness predictor, a 0–10 perception scale or the five-level personalization threshold. No product code, UI, scoring weights, campaign economics, saved model or research result was changed in this phase.

## Evidence by component

| Component | Current evidence | Readiness |
| --- | --- | --- |
| Text cue screen | Phase 11 synthetic fixtures: 18 TP, 1 FP, 2 FN, micro F1 0.923. Phase 12 project-authored real-ad holdout: 0 TP, 0 FP, 2 FN for the only two positive pressure cues among 11 assessable ads; precision undefined, recall 0/2 with a very wide interval. | **Experimental screening only.** Limited time phrasing is missed; seller contact is misread as viewer identity on development copy. No positive privacy holdout. |
| Image OCR and cue pipeline | Ten licensed real images inspected. OCR can lose visible deadlines or create false contact-number cues; two missed time-limit creatives abstain, while one seller phone produces a false high 6/10. | **Review aid, not reliable unattended image classification.** No validated CER/WER or visual object understanding. |
| A–E budget and STP planner | Phase 11 synthetic 18-state decision and financial stress checks; Phase 12 full regression rerun under the documented alternative SAV reader. | **Working advisory prototype.** Costs, break-even and hypothetical scenarios are arithmetic on marketer inputs, never uplift estimates. Keep is compared before adding variants; permission/source mismatches hold. |
| Research dashboard and V1/V2/Criteo/other saved work | Original source/model/result preservation manifest verifies 604 files; Phase 7 SAV aggregate replay matches saved result exactly with the approved alternate reader. | **Descriptive/research context only.** No survey-to-campaign audience matching. |
| Mode B audience schema | Offline input-contract checks only; no live customer-file upload. | **Not operational.** |
| Five personalization levels | No same-exposure direct intrusion × engagement estimates for five eligible assigned levels. | **Unsupported for recommendation**; engine returns `insufficient_evidence`. |

The real-ad annotations were made in one AI-assisted project pass and are not independent human or Tier C cue labels. The Mendeley CSV is publisher-extracted text, not verified OCR truth. The selected source is mainly Arabic and has no ad-specific targeting or direct consumer discomfort response. The Phase 12 test was viewed once and the rubric was left frozen rather than adding phrases to improve a tiny holdout score. An apparent high synthetic F1 and a zero real-ad recall can coexist because their sampling and label sources differ substantially; neither estimates consumer-specific discomfort.

## Product and research priorities

1. Obtain properly licensed, independently cue-annotated ad copy/images with enough **positive privacy and pressure** cases and verified transcripts. Define English and other-language scopes before testing. Keep unseen creatives untouched during rule work.
2. Resolve referent ownership for phone/email, distinguish deadlines from generic CTAs, and test negation, quotation and rhetorical scarcity on a new development collection. Only then run a new held-out set; do not retune on Phase 12's final IDs.
3. For perception and personalization, identify secondary data linking assigned treatment, specific exposed creative, direct intrusiveness, relevance and engagement in the **same eligible observations**, with reuse rights and privacy safeguards. Until then keep the threshold abstaining and the score labelled exploratory.
4. If image analysis is advanced, collect verified image text transcriptions and evaluate OCR separately by resolution, orientation, contrast and language. Do not infer image objects or tracking from OCR.

The native Windows `pyreadstat` DLL remains policy-blocked. The full suite succeeds only with the explicit R-backed test-runtime adapter; see [environment recovery](PHASE12_REGRESSION_ENVIRONMENT_RECOVERY.md). No real-browser retest was triggered because no app or interface code changed; Phase 11 browser checks remain historical, not Phase 12 usability evidence.
