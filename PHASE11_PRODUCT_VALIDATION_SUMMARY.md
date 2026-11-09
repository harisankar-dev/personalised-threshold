# Phase 11 — product validation summary

**Readiness, 9 November 2026:** The Mode A marketer app is a working, explainable **pre-launch advisory prototype**. Phase 11 validated selected software and business-rule behaviour through synthetic tests and a real browser walkthrough. It did **not** validate consumer-perceived intrusion, actual engagement uplift, legal compliance, audience segmentation or the five-level personalization threshold.

## What was measured

- A frozen 26-case, author-defined synthetic cue set produced 18 true positives, 7 false positives and 2 false negatives before the change. A narrow negation guard yielded 18/1/2 and micro F1 **0.923 versus 0.800** on those same fixtures. This is **diagnostic fixture performance**, not independent real-ad precision or consumer intrusion accuracy. Two implicit/sensitive paraphrases remain missed, and rhetorical scarcity remains a false alarm.
- A synthetic **18-state** STP decision matrix plus an OCR-empty hold checked keep/revise/hold precedence, source and consent gates, affordability, the current-campaign comparator and hypothetical-scenario nonpromotion. All expected actions passed.
- Decimal stress tests confirmed exact A–E costs, headroom, break-even rounding and hypothetical net arithmetic. They caught a fractional-cent display inconsistency, now rejected. Tiny reach gets a clearer fragmentation warning. No scenario was treated as a forecast.
- The real browser showed the key text/image, consent, budget, error-recovery and 390-pixel layout paths. This is expert inspection, not marketer participant research.

## What improved and what remains unsupported

The cue screen better handles local denials and quotes; the budget engine rejects sub-cent money; the keep reason warns when targeting context is missing; permission choices state they are marketer declarations; suggested edits and one-conversion copy no longer imply more certainty than available. API names, 0–10 weights/cutoffs, saved research artifacts and the five-level abstention remain intact.

No independent cue-labelled ad set matching the rubric was established from the local permitted sources. The CHI ad-perceptions files have a different label system and no verified local reuse terms for this exercise. No direct consumer-rating dataset connects arbitrary uploaded creatives, targeting declarations and observed outcomes. Therefore a high synthetic cue F1 cannot establish a dependable intrusion classifier, and the current app cannot choose profitable customer segments. Phase 9/10 OSF rights and privacy gates remain closed; no respondent-level files were opened, no new ML model was trained, and Mode B stays an offline schema validator.

## Most useful Phase 12 direction

First obtain a genuinely reusable, **independently cue-annotated diverse ad set** and evaluate text and OCR by creative family, quotation/negation, channel and language with held-out examples. Separately, only if rights and privacy are documented, evaluate direct consumer intrusiveness, relevance and actual engagement for the **same specific exposures** and an eligible audience. Keep the creative screen and STP advisory as distinct layers until those measurements support a narrow, externally checked promotion. The default financial choice should remain the least costly justified change within the fixed budget.
