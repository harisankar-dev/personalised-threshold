# Phase 11 — budget stress test

The calculator in `stp_advisory.py` uses user-entered `Decimal` amounts in one declared currency. It does **not** convert currencies, reallocate existing media spend, add future media spend, predict conversions or optimize profit. Any company using several currencies must convert amounts consistently before entry.

## Exact arithmetic and included costs

Headroom = total budget − already committed spend, only when both are known. A known option cost is affordable when it does not exceed that headroom. The current campaign is always Option A with zero **incremental implementation** cost, not zero total campaign spend.

| Option | Incremental cost |
| --- | --- |
| A Keep current campaign | 0 |
| B Revise one creative | Revision cost |
| C Adjust targeting | Targeting cost + additional management cost |
| D One extra variant | Per-variant creative cost + additional management + segmentation cost |
| E Multiple variants | Number of **additional** variants × per-variant cost + additional management + segmentation cost |

With a positive known contribution margin, break-even extra conversions = `ceil(option incremental cost / margin)`. A hypothetical net incremental value = user-entered extra conversions × margin − the selected option's incremental cost. These calculations exclude baseline media spend because it is held fixed, and exclude any unentered cost. Missing cost or margin remains `Unknown`; zero margin produces no break-even count. All scenario values are explicitly hypothetical and cannot trigger a rollout recommendation.

## Numerical stress results

The new synthetic financial test entered a 1,000.00 total budget, 900.00 committed, 20.00 revision, 30.00 targeting, 40.00 each extra creative, 15.00 segmentation, 5.00 management, three additional variants and 12.00 contribution margin. Headroom was **100.00**. A–E extra costs were **0.00, 20.00, 35.00, 60.00, 140.00**; break-even counts were **0, 2, 3, 5, 12**; E was over budget while A–D fit. For D, hypothetical 0/5/6 extra conversions produced **−60.00 / 0.00 / +12.00** incremental net values. The advisory still kept the low-cue current campaign because those conversions were not observed uplift.

Other executed tests covered zero and fully committed budgets, overspend rejection, missing/zero margin, high revision cost, multiple variants, negative/nonfinite values, invalid currency format, audience reach too small even for one distinct person per variant, and an extreme permitted **1,000,000,000,000.00** budget with cent-exact arithmetic. For the latter, 10.00 headroom and 9.99 revision cost left **0.01**, with 999 extra conversions needed at a 0.01 margin. Amounts with fractional cents (for example 0.005) are now explicitly rejected instead of being calculated at sub-cent precision and displayed as rounded cents. The currency label is retained unchanged in the output; its economic consistency remains the marketer's responsibility.

The app now warns when declared reach is less than the current creative plus the entered additional variants. Reach alone still does not establish response counts, valid segmentation, adequate power or returns from extra creatives. The real-browser walkthrough showed a 100.00 budget with 90.00 committed: a 20.00 revision was **over budget** and held; at 5.00, it was **within budget** and suggested as one revision. A positive user-entered scenario remained labelled hypothetical. No actual uplift or ROI was measured.
