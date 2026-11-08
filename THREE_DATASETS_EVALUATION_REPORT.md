# Three supplied secondary datasets: evaluation and integration

**49-C | 7 November 2026 | Secondary data only**

## Decision

All three supplied ZIP archives are valid and reusable under their publishers' CC BY 4.0 terms, but their five extracted files are byte-for-byte identical to files already under `try these dataset/`. They add **zero independent respondents**. The Romano–Han survey is already used in V1–V3. The Gen Z workbook is already covered by the V1 descriptive audit. The Vietnam survey adds a useful, **separate descriptive** privacy/trust/purchase-intention analysis. None supplies a five-level exposure treatment paired with a direct intrusion response. The threshold engine must continue to return `insufficient_evidence`.

| Supplied archive | Decision | Exact contribution |
| --- | --- | --- |
| Vietnam privacy-practices survey | **Use Separately** | Documented scale reliability and predeclared privacy/trust/intention associations; no ad-level or intrusion model. |
| Personalized social-media ads, Gen Z | **Use Separately** | Retain existing descriptive V1 associations, with additional coding and birth-year caveats; no new model. |
| `zcp5httw5c-1.zip`, Romano–Han | **Use** (existing V1–V3 only) | Direct respondent-level general-ad intrusion items. Its ZIP is a duplicate, so it is not a new external validation set. |

## Provenance, files, permissions, and safe extraction

The publisher records are [Vietnam privacy practices](https://data.mendeley.com/datasets/2x8xnfbsfd/2), [Gen Z personalized social-media advertising](https://data.mendeley.com/datasets/czgx8b793m/1), and [consumer perceptions of unsolicited social-media ads](https://data.mendeley.com/datasets/zcp5httw5c/1). Each publisher record advertises **CC BY 4.0**, which permits reuse with attribution. Keep their original citation and license details with any public redistribution; this report links to each source. These are secondary observational survey records, not project-collected responses.

The three original ZIPs were copied unchanged to `secondary_data/user_supplied_2026-11-07/archives/`. `three_user_datasets_audit.py` verifies each expected archive SHA-256, checks ZIP CRCs, forbids path traversal and links, enforces a size bound, and refuses to overwrite extracted files. It extracted five files into versioned directories. `results/three_user_datasets_audit_v1.json` records each entry's hash, shape, missingness, duplicate count, and exact local counterpart. All five SHA-256 values match the corresponding pre-existing files. Neither the existing files nor original archives were modified.

| Dataset / file inspected | Rows × columns | Missing cells | Identical full response rows | Existing counterpart |
| --- | ---: | ---: | ---: | --- |
| Vietnam CSV | 467 × 32 | 0 | 0 | Same CSV in `try these dataset/` |
| Vietnam `Questionnaire for data.pdf` and `CODEBOOK.pdf` | Two 2-page documents | — | — | Same two PDFs in `try these dataset/` |
| Gen Z `GenZ_Personalized_Ads_Purchase_Dataset_N296.xlsx` | 296 × 35 | 0 | 1 | Same workbook in `try these dataset/` |
| Romano–Han `Consumer perceptions towards unsolicited ads on social media.sav` | 837 × 27 | 0 | 2 | Same SAV in `try these dataset/` |

An identical full response does not prove the records are the same person; no row was automatically dropped. Record identifiers must not be joined across surveys. The ZIP names, paths, individual file hashes and all 35 workbook column names are in the machine-readable audit. Before extraction, the project had no Git repository; recoverable file-and-hash checkpoints were created at `baselines/phase5-start-2026-11-06/` and `baselines/three-user-zips-start-2026-11-07/`.

## Measurement map and fit to 49-C

| Concept | Vietnam privacy practices | Gen Z personalized ads | Romano–Han unsolicited ads |
| --- | --- | --- | --- |
| Unit | Online-market respondent in Vietnam | Gen Z respondent reporting social-media ad experiences | Respondent rating unsolicited social-media ads in general |
| Customer behaviour | Self-reported online purchase frequency `q4`; purchase **intention** `IB1–IB4` | Online shopping frequency, reported last-30-day ad click/purchase codes; purchase tendency items | Ad avoidance `AAB` and ad-benefit `PAB` scales |
| Privacy | Collection `COL1–4`, data error `ERR1–4`, unauthorized secondary use `USU1–4`, improper access `IMA1–3` | Four personalized-ad privacy concern items | Same-wave privacy concern `PC1–PC6` |
| Trust | Online-store trust `OT1–4` | No documented comparable trust scale | No directly comparable online-store trust scale |
| Personalization | None | Five **perceived** personalization items, no assigned dose or exposure | No assigned dose or exposure |
| Intrusiveness | None | None; privacy concern is a different construct | **Direct** general-ad intrusion `I1–I6`, 1–7 agreement scale |
| Engagement | No observed ad engagement | Self-report ad click/purchase codes with incomplete code-direction metadata | Ad avoidance self-report, no per-ad engagement |
| Five-level treatment and response on same unit | **No** | **No** | **No** |

The Vietnam questionnaire's first three yes/no screening questions are `q1` ever purchased online, `q2` affected by improper personal-information use, and `q3` concerned about privacy. Every retained row answers code 1 (yes), so this selected sample cannot estimate those prevalences. The `q5` prompt says **select all that apply** for seven concern categories, whereas the CSV stores a single integer (observed codes 1–5); its intended multi-response meaning cannot be reconstructed, so it is excluded from analysis. Scale items have documented 1–5 agreement anchors. No ad or actual purchase outcome is observed.

The Gen Z workbook contains Turkish wording for perceived tailoring, relevance, usefulness, novelty, privacy concern, and purchase tendency. Its click and post-ad purchase codes are not accompanied by an unambiguous value-to-answer mapping; those fields are not used as supervised outcomes. The publisher description calls the respondents adults aged 18–29 yet also gives a birth-year range of 1997–2012. The workbook includes 18 records with 2009–2012 birth years. Without a documented collection date or coding explanation, adult status for those records cannot be verified. This does not invalidate the whole workbook, but it further limits behavior-outcome modelling and subgroup claims.

The Romano–Han source has the strongest match to the **intrusion response** construct and is already the source of the separate V1, V2 and V3 research experiments. It asks about unsolicited ads in general rather than showing scored ad creatives or assigning five levels. Privacy and intrusion are recorded in the same questionnaire, so shared wording and common-method effects can inflate apparent prediction. Reusing the identical ZIP as a fresh test would be data leakage.

## New, appropriate analysis: Vietnam scale audit

`vietnam_privacy_trust_v1.py` verifies the source hash and questionnaire-implied 1–5 scale bounds; excludes constant screening responses, the record number, and ambiguous `q5`; computes six item-mean scales; and calculates Cronbach's alpha. Four associations were fixed before running the analysis and use Spearman's rho with 2,000 seeded respondent-bootstrap resamples for a descriptive 95% interval. The script creates `results/vietnam_privacy_trust_v1.json` and refuses to overwrite it. It trains no model because this source has neither the project's intrusion target nor an ad-level deployment decision.

| Scale | Items | Alpha | Mean (1–5) |
| --- | ---: | ---: | ---: |
| Collection concern | 4 | 0.859 | 3.970 |
| Data accuracy concern | 4 | 0.877 | 3.779 |
| Unauthorized secondary-use concern | 4 | 0.929 | 3.911 |
| Improper-access concern | 3 | 0.880 | 4.145 |
| Online-store trust | 4 | 0.901 | 3.858 |
| Purchase intention | 4 | 0.808 | 3.845 |

| Predeclared association | Spearman rho | Respondent-bootstrap 95% interval |
| --- | ---: | --- |
| Collection concern / online trust | 0.224 | [0.133, 0.317] |
| Secondary-use concern / online trust | 0.333 | [0.250, 0.416] |
| Online trust / purchase intention | 0.450 | [0.364, 0.529] |
| Collection concern / purchase intention | 0.453 | [0.371, 0.531] |

Trust/intention correlation by coded age group is 0.429 (n=123), 0.508 (n=120), 0.483 (n=115), and 0.378 (n=109) for groups 1–4. These are within-sample descriptions, **not causal effects, independent validation, prevalence estimates, or predicted ad intrusiveness**. Positive privacy/trust correlations should not be given a causal story. The intervals account for row resampling only; they do not correct sample selection, survey response style, multiple testing, or common-method bias. No train/test split is appropriate without a defensible predictive target; avoiding a meaningless model is an intentional leakage/overfit control.

## Relationship to existing models and remaining threshold barrier

The Romano–Han V1 ridge model's held-out MAE was 0.521 versus a training-mean 0.815 baseline; V2 achieved 0.509 but its paired improvement interval crosses zero and it missed more high-intrusion cases below the agreement boundary. These results remain respondent-level experimental findings. The Vietnam and Gen Z respondents are unrelated to that sample; their questionnaire items and response scales are incompatible with direct pooling or score transfer. Their presence does not change V1/V2/Criteo results, the creative screen, the app, or the threshold engine.

To identify a **five-level personalization threshold**, secondary records would need verified variation across the five exposure levels and a direct per-exposure intrusion response on the **same observational unit**, with consent/context and ideally engagement measured alongside, plus a fresh holdout or independent compatible validation. None of the three ZIPs provides that joint measurement. Current readiness remains **`insufficient_evidence`**.

## Reproduction, tests, and file changes

Use the environment described in `PHASE5_MODEL_VALIDATION_REPORT.md`. Run `python three_user_datasets_audit.py` on a fresh versioned extraction destination, then `python vietnam_privacy_trust_v1.py` on a fresh versioned output destination; both refuse silent replacement of existing outputs. In this workspace the saved results are immutable versioned artifacts. `test_three_user_datasets_audit.py` checks safe ZIP path handling. `test_vietnam_privacy_trust_v1.py` checks that the prepared data exclude constant/ambiguous fields. The Vietnam script was separately replayed to a temporary output, with an **exact JSON result match**. The full regression suite passed **41/41** tests; the Phase 5 replay reproduced all **seven** saved research outputs. Neither replay provides an independent validation sample.

Created for this evaluation: `secondary_data/user_supplied_2026-11-07/` (three unchanged archive copies plus five safely extracted files), `baselines/three-user-zips-start-2026-11-07/`, `three_user_datasets_audit.py`, `test_three_user_datasets_audit.py`, `results/three_user_datasets_audit_v1.json`, `vietnam_privacy_trust_v1.py`, `test_vietnam_privacy_trust_v1.py`, `results/vietnam_privacy_trust_v1.json`, and this report. Existing datasets, V1/V2/Criteo artifacts, and app models were not overwritten.
