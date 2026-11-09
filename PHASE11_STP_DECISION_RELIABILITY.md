# Phase 11 — STP decision reliability

**Scope:** deterministic business-rule behavior for declared campaign inputs and heuristic creative cues. A correct `keep`, `revise` or `hold` result is not proof of safe targeting, consumer comfort or incremental business value.

## Action precedence and decision table

| State | Expected action | Evidence and limit |
| --- | --- | --- |
| Source/method conflict, unresolved personal-data source, sensitive method, declared ineligible audience, explicit lack of consent, or required permission/eligibility not declared yes | `hold_for_review` | The fields are marketer declarations; the app cannot verify a legal permission or real audience eligibility. Positive what-if outcomes cannot override this hold. |
| No assessable creative text, including OCR-empty image | `hold_for_review` | Visual objects and page obstruction remain unassessed. |
| Moderate/high cue total and a known revision cost above known headroom | `hold_for_review` | Do not advise an unaffordable revision. |
| Moderate/high cue total without the above blockers | `revise_one_creative` | Editorial suggestion to revise and test one creative; financial benefit remains unknown if margin or budget is missing. |
| Low cue total without blockers | `keep_current_campaign` | The current campaign is the comparator; missing method/source information is now called out in the main reason before launch. No extra segmentation is justified. |

The [Phase 11 test matrix](test_phase11_product_validation.py) exercised **18 campaign states**: generic and low-risk copy; moderate affordable revision; high cues without headroom; unknown and mismatched sources; behavioural consent and historical eligibility gaps; sensitive method; apparently affirmative but **self-reported** permissions; contradictory declarations; missing margin; positive hypothetical gain; tiny reach; variants over budget; unaffordable revision; permission versus gain; and an explicit no-consent copy cue. All 18 returned the expected action. A separate `needs_review` case verified the OCR-empty hold. Existing Phase 7/8 suites cover API route compatibility, data-source review, survey separation and threshold abstention.

## Defects and bounded fixes

- A low-cue ad with both targeting method and source omitted returned `keep_current_campaign` with warnings, but its **main reason** could read like launch reassurance. It now names the current campaign as a **cost comparator** and tells the marketer to review missing targeting information before launch. The action name is preserved for API compatibility.
- The original interface called a `yes` permission selection simply “Verified.” The form now says **“I declare permission verified”** and **“I declare audience eligible.”** The backend still treats these as declarations and provides no compliance certification.
- Explicitly denied targeting data could contribute false cue points. The local denial guard removes those narrow false alarms while allowing a later positive use in another clause. This affects the cue-based action only through the existing thresholds; there is no score recalibration.

## Preserved invariants

Option A, `keep_current_campaign`, remains first in every comparison. C–E are shown for cost comparison but are never automatically recommended from unrelated survey profiles. Declared permissions are unverified by the software. The scenario fields are user-entered hypotheses and cannot become observed outcomes. There is no conversion-lift prediction, automatic ad publication, real Mode B upload or customer-segment assignment. The five-level threshold remains `insufficient_evidence`. The app's legacy `/api/analyze` response remains compatible when no campaign object is supplied.
