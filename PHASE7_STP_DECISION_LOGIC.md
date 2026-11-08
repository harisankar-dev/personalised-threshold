# Phase 7 — minimum-change STP advisory contract

**Status:** An explainable business-rule advisory and calculator. It is **not** a validated predictive targeting or personalization-threshold model. Implementation: `stp_advisory.py`; optional integration: `POST /api/analyze` with a `campaign` object. If `campaign` is absent, the pre-existing response schema remains unchanged. `threshold_engine.py` is untouched and still returns `insufficient_evidence` on current data.

## Input and evidence contract

The existing creative screen returns visible **text/OCR cue matches**, an exploratory three-tier score and cue-linked editing suggestions. The `campaign` object can declare `objective` (`unknown`, `awareness`, `traffic`, `conversions`); `targeting_method` (`unknown`, `generic`, `contextual`, `demographic`, `behavioral`, `historical`, `combined`, `sensitive`); `consent_status` and `audience_eligibility` (`unknown`, `yes`, `no`); and a three-letter `currency`. These are **marketer declarations**. Free-text `targeting` is still screened for cue wording, but the structured method/permission check uses only structured fields; neither is independently verified.

All amounts are optional, non-negative user inputs. `total_budget` is the **entire ceiling** and includes existing media/operating spend plus any incremental production, management and segmentation expense. `committed_spend` is the amount already committed to the current campaign. Budget headroom = total budget − committed spend, when both are supplied. The calculator assumes **no extra media spend and no reallocation of existing media**; if those change, its net-value arithmetic is incomplete. Amounts use `Decimal`; there is no exchange-rate conversion. A negative, nonfinite or inconsistent amount produces a client error. Missing data stay `null`/`Unknown`, never default zero. `cpc`, `cpm`, `conversion_rate_pct` and `audience_reach` are accepted as baseline context but do not create an uplift estimate. `contribution_margin` is required for break-even math; conversion rate alone cannot stand in for contribution profit. The objective is recorded and flagged when absent; because no option-specific effect is validated, it does not drive a numeric optimization. For awareness/traffic objectives, conversion break-even is explicitly labelled as a financial check rather than the campaign's validated success measure.

### Incremental-cost comparison

| Order | Option | Additional implementation cost when all components are known |
|---:|---|---|
| A | Keep current campaign | 0 |
| B | Revise one existing creative in the same campaign | `revision_cost` |
| C | Adjust targeting in the same campaign | `targeting_cost + management_cost` |
| D | Test one extra creative variant | `variant_cost + management_cost + segmentation_cost` |
| E | Consider multiple segment-specific variants | `variant_count × variant_cost + management_cost + segmentation_cost` (`variant_count` ≥2) |

Costs are **additional**, not total campaign spend. Option A is always listed. An option is within the entered budget only when both headroom and its full additional cost are known and cost ≤ headroom; otherwise affordability is `Unknown` or `Over budget`. The table shows a **separate permission column**: `Hold for review`, `Unverified`, or `Declared eligible` based solely on the marketer's declarations and visible no-consent cue. Budget feasibility never overrides a permission hold. A break-even number is calculated only if cost is known and `contribution_margin > 0`: `ceil(additional_cost / contribution_margin)`. This is minimum extra conversions for nonnegative *incremental contribution*, assuming media spend and margin per conversion remain unchanged. It is not an expected conversion count or the number needed to guarantee a profitable campaign. If margin is absent or zero, break-even is `Unknown`.

The optional `scenario_option` chooses B, C, D or E and accepts user-entered non-negative integer `worst_incremental_conversions`, `central_incremental_conversions`, `best_incremental_conversions` (ordered if all present). For each supplied number with a known margin and cost, **net incremental value = extra conversions × contribution margin − additional implementation cost**. These numbers are explicitly **hypothetical sensitivity inputs**. Positive central or best-case arithmetic does not change the advisory action, because the project has no validated segment-specific uplift. No ROI/ROAS, CTR or conversion improvement is invented.

### Advisory action order

1. `hold_for_review` if the declared method uses sensitive personal data, the audience is declared ineligible, the copy explicitly indicates no consent, or a demographic/behavioral/historical/combined method lacks **both** verified permission and eligibility. The code does not infer consent from survey attitudes.
2. `hold_for_review` when an image/text creative has `needs_review` and no assessable cue conclusion. For a moderate/high cue creative, also hold if a known revision cost exceeds known headroom.
3. `revise_one_creative` as **editorial advice** when the creative has moderate/high cue points and no blocking condition. The suggestion is to revise and test **one** creative within the existing campaign. If budget/cost is missing, affordability remains unknown; the action is not a claim that revision pays for itself.
4. Otherwise `keep_current_campaign`: “Available evidence does not justify additional segmentation costs.” This is a conservative *comparison recommendation*, not a certification that an unknown ad or audience is launch-safe. Missing targeting, consent, budget and reach produce explicit warnings.

Options C–E are compared economically but are **never automatically recommended** by current data: no survey profile can be linked to consented campaign records, and Criteo's binary treatment does not validate their audience-level incremental benefit. A known audience reach alone does not establish adequate per-variant response volume; fragmentation risk stays flagged. No protected or sensitive demographic is used for exclusion. The five conceptual personalization levels remain in the separate threshold contract with no per-level estimates.

## Application interface and output labels

The existing text/image flow, OCR, creative `tier`, `score_out_of_10`, matched `evidence`, `recommendations`, and `threshold_decision` remain. When `campaign` is present, the response adds `strategy`, including `action`, `reason`, `options`, explicit `missing_inputs`, optional `scenario`, budget scope, and `survey_personas`. The latter contains **only counts and shares** from `results/phase7_segmentation_v1.json`, split by source, with `status: descriptive_only`. No survey respondent rows, identity matching, persona probabilities or ad-specific suitability scores are returned. The UI labels the action as **Exploratory**, names the scenario hypothetical, and keeps the threshold notice visible.

The calculator's financial values, consent status and campaign context are provided by the marketer and are not persisted by the local app. The page makes no real campaign changes, sends no ads to an external API and never publishes a creative. UI request validation still rejects malformed text, oversized images and spoofed image signatures as before.

## Readiness boundary

The economic formulas and permission/eligibility gates are software rules with regression tests. They do **not** establish that any revision increases engagement or that the computed survey profiles are operationally targetable. A future action beyond one-copy editorial review needs a compatible secondary source or authorized first-party pilot data with impression denominator, actual creative/method, consented customer attributes, direct intrusion, relevance and engagement on the same exposure, then independent evaluation of false reassurance and net benefit. Until then, keep the threshold at `insufficient_evidence` and treat C–E as scenarios, not rollout recommendations.
