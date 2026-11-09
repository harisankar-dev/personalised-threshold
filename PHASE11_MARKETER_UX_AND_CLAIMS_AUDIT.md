# Phase 11 — marketer UX and claims audit

This is an **expert browser walkthrough and heuristic inspection**, with no marketer participants, task-completion measurements or satisfaction scores. The local app was tested in a real browser on 9 November 2026.

## Workflow and evidence labels

A marketer enters ad copy or an image, optionally supplies visual description and targeting details, declares campaign context and may enter budget/cost and hypothetical conversion scenarios. The output distinguishes matched text/OCR cues and a heuristic 0–10 rubric, **declared** targeting/permission fields, unrelated aggregate survey profiles, cost arithmetic and hypothetical what-if values. It says that consumer relevance, discomfort, causal uplift and the five-level threshold are unknown. The page does not claim guaranteed ROI, legal compliance or a best audience segment.

The form makes most campaign inputs optional and shows unknown affordability rather than silently using zero. Headline/body guidance, OCR-only caveat, budget scope, `needs_review` state, cue explanations, repair suggestions, source warnings, and an A–E comparison are visible. The table can scroll within its container; the page itself did not overflow at a **390 × 844** test viewport. Read-only browser geometry found a 390-pixel viewport, 375-pixel document width and 301-pixel primary inputs. This is a responsive layout check, not a usability study or accessibility certification.

## Actual browser walkthrough

| Input | Observed outcome |
| --- | --- |
| Generic text example | Low tier, 0/10; current campaign shown as comparator with missing targeting and budget caveats. |
| `We tracked you across shopping sites` | Moderate tier, 5 privacy points, explicit tracking match and one-copy revision advice. |
| `Last chance! Only 3 left! 99% off!` | High tier, 6 pressure points, three matched cues and separate pressure breakdown. |
| `Never say 'last chance' in our ads` | Low tier, 0 cues after the local denial fix. |
| Supplied aggressive PNG | Real local OCR returned high tier, displayed cap 10/10 from 12 pressure points and six cue explanations; visual objects remained unassessed. |
| Plain white synthetic PNG | OCR found no text; `needs_review`, no number, and a hold with a prompt for visual description. The disposable fixture was removed after testing. |
| Behavioural method, missing source despite affirmative declared permission | `hold_for_review`; source uncertainty explained. |
| Behavioural source with unverified consent | `hold_for_review`; permission warning visible. |
| 100 budget / 90 committed / 20 revision | Headroom 10, revision over budget, `hold_for_review`. |
| Same budget / 5 revision and positive hypothetical case | Revision within budget, one-copy suggestion; what-if values still labelled hypothetical. |
| Committed spend above total budget | Recoverable form error; correcting the value returned to a normal result. |

## Changes and remaining ambiguity

The permission and eligibility choices now say **“I declare …”** so the UI does not imply the application verified legal or audience status. The repair heading changed from “Ways to lower risk” to **“Suggested copy edits”**, matching the absence of consumer-effect evidence. The keep action's main reason now warns when targeting method or source is omitted. The what-if display now uses **“1 extra conversion”** for a single hypothetical conversion. These are small presentation changes; the form and architecture were not redesigned.

Remaining issues: the interface is dense for a first-time marketer; some warnings are long and the desktop comparison table scrolls horizontally inside its panel. OCR may miss stylized text and cannot judge layout or images without text. A low cue score means no current pattern matched, not that the creative is comfortable or compliant. The denial guard cannot resolve sarcasm, all quotation scopes or implicit tracking. Permission declarations still require external verification before a real launch decision. No automated accessibility audit, assistive-technology session or user research was performed.
