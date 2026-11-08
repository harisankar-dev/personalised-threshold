# Phase 9 — data rights, privacy and source eligibility

**49-C | Reviewed 8 November 2026 | Secondary data only.** This review is a research-data intake decision, not a legal opinion or a claim that public access grants model-training rights. No OSF respondent workbook was downloaded, retained, redistributed or used to fit a model in Phase 9.

## OSF source and current rights check

The most relevant source remains [Verenkotte and Spann, *How Information-Use Transparency Affects the Effectiveness of Location Targeting*](https://www.tandfonline.com/doi/full/10.1080/00218499.2026.2709216), DOI `10.1080/00218499.2026.2709216`, linked by the article to [OSF project `zv8xy`](https://osf.io/zv8xy/). The article gives a public data-and-code availability link; that statement is not a dataset license. The [OSF node API](https://api.osf.io/v2/nodes/zv8xy/) returned `license: null` and `public: true` on this review. The node showed last modification on 22 July 2026. The [replication README](https://osf.io/download/tw6dm/) describes folders and R execution steps but states no reuse, derivative-model, redistribution, retention, attribution or commercial terms. [OSF's licensing guidance](https://help.osf.io/article/148-licensing) explains why an explicit license matters. The publisher's article access and any article license do not resolve rights to the separate respondent workbook.

The OSF public file tree still lists `study1_data.xlsx`, `study2_data.xlsx`, `study3_data.xlsx`, a pooled Study 1/2 workbook, R scripts and the README. **No separately labelled identifier-minimized release or data license was found** in that listing or README. This is a statement about the checked records, not proof that the authors have no private minimized copy. Study 1 is the no-versus-city location-targeting 2×2 experiment; Study 2 is country-versus-city targeting crossed with disclosure. Phase 8 inspected 409 and 401 respondent rows in memory, with direct `PPI` intrusion, `PPR` relevance, `PP` personalization and `ITC` click intention in each experiment. Study 3 has four **aggregate ad-set** rows. The pooled workbook is not an independent sample. [Phase 8's schema/quality audit](PHASE8_SECONDARY_EVIDENCE_SEARCH.md) contains the field list and earlier non-retained descriptive inspection. Phase 9 did not reopen or copy those raw workbooks.

**Decision:** Explicit permission for this proposed secondary academic analysis, model training/retention and derivative publication has **not** been established. Public access alone is insufficient for the intended reuse. OSF respondent-level data are **ineligible for Phase 9 training**. An explicit author grant or a clearly licensed, appropriately minimized release would need a fresh documented review before that decision changes. No permission request was sent.

## Privacy and data-handling gate

The original Study 1/2 exports were previously found to contain raw IP addresses, location coordinates, `ResponseId` and `PROLIFIC_PID`. These are not needed to estimate a location-condition response. IP and precise location can reveal or help infer a participant's identity; a public file is not automatically a safe model-training file. The proposed minimized release should omit IP, precise coordinates, platform IDs and unnecessary free text, technical metadata and timestamps. If repeated measures exist, the author can supply a new study-local pseudonymous grouping key; the mapping must stay with the data provider. Retain only declared treatment codes, validated response items, justified pre-exposure features and any necessary non-identifying stimulus/group key. Check small-cell disclosure risk before sharing aggregates or artifacts.

**Retention decision now:** keep no OSF row-level workbook, extract, cache, model or participant identifier in the 49-C project or Git repository. The public URLs, file names, rights decision and an unsent permission request are retained as documentation. If a permitted minimized release arrives later, store it in a separate restricted location, record the grant, provenance and retention period, verify data minimization before loading it, and publish only outputs the grant permits. No automatic customer upload or audience matching follows from research permission.

## Alternative licensed-source screen

The machine-readable [candidate matrix](phase9_research/candidate_matrix.csv) records seven screened sources, the required measurements and the decision. Publisher/repository records were checked rather than relying on titles.

| Source | Explicit data terms | Direct intrusion and assigned personalization treatment in the same record? | Phase 9 decision |
|---|---|---|---|
| [Romano–Han, 837 US respondents](https://data.mendeley.com/datasets/zcp5httw5c/1) | CC BY 4.0 | General unsolicited-social-ad intrusion; **no assigned ad treatment or specific creative** | Retain separate prior survey research; no new experimental model. |
| [Redondo–Aznar, 1,511 respondents](https://data.mendeley.com/datasets/89nk3kp8tg/1) | CC0 1.0 | General online-ad interruption; **no assigned personalization treatment** | Retain separate prior benchmark. |
| [Gen Z personalized-ad survey, 296 rows](https://data.mendeley.com/datasets/czgx8b793m/1) | CC BY 4.0 | Relevance and privacy concern; **no direct intrusion or randomized ad** | Retain descriptive context only. |
| [Criteo Uplift](https://huggingface.co/datasets/criteo/criteo-uplift) | CC BY-NC-SA 4.0 | Binary ad treatment and behavior; **no intrusion/relevance or creative** | Keep prior isolated benchmark; noncommercial/share-alike terms remain relevant. |
| [Kim–Ha backfire experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC12561546/) | Respondent data on request | 3×2 messages/privacy prime and purchase intention; **no measured intrusion target** | Exclude from training. Its three messages are not 49-C's five levels. |
| [Elsen–Pieters–Wedel ad-typicality experiment](https://data.mendeley.com/datasets/dry79fnv2z/2) | CC BY 4.0; data description and stimuli listed | Assigned ad typicality/exposure schedule; **no privacy-intrusion or personalization outcome** | Exclude from this target despite usable license. |

No screened source simultaneously supplied an explicit usable license, privacy-safe individual records, an assigned ad personalization condition, a direct post-exposure privacy-intrusion outcome and a compatible specific-ad response. The licensed sources cannot be merged with OSF or each other by arbitrary respondent IDs. The additional search stopped here because further general ad-engagement datasets would not close the defined validation gap.

## Contact and next decision

The [publisher article page](https://www.tandfonline.com/doi/abs/10.1080/00218499.2026.2709216) publicly lists **Johanna Verenkotte, `verenkotte@lmu.de`**, at LMU Munich. This is the verified contact source; no address was inferred from a naming pattern. [The prepared email](PHASE9_OSF_DATA_PERMISSION_REQUEST.md) asks for an identifier-minimized release and explicit academic analysis, model, derivative, attribution and commercial-use terms. **Status: draft only; not sent.**

The next data gate is a written permission or published dataset license plus a reviewed minimized release. Only then should the narrow experimental protocol in `PHASE9_EXPERIMENTAL_INTRUSIVENESS_REPORT.md` be run. The general marketer app, optional Mode B design and five-level threshold gain no validation from the present rights check.
