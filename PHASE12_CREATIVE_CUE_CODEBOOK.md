# Phase 12 real-ad creative cue codebook (v1)

**Unit:** one advertisement's visible/recorded copy. Labels describe *wording present in a creative*, never a consumer's perceived intrusiveness, a targeting practice actually used, or offer truth. The only real-ad source used here is Salem et al., *Advertising Images Dataset for Visual Analysis*, v1, DOI [10.17632/32grwbk6rv.1](https://data.mendeley.com/datasets/32grwbk6rv/1). Its CSV `text` field was semi-automatically extracted by the publishers. Their quality and CTA scores are **not cue labels**.

## Four states

For every cue, record `present`, `absent`, `ambiguous`, or `unassessable`. `Absent` means the assessable English copy does not assert the cue; it does **not** prove the campaign is safe. `Ambiguous` means the wording supports competing readings. `Unassessable` means the image/text is missing, illegible, or in a language the current English detector and this annotation pass cannot reliably assess. Exclude ambiguous and unassessable cue instances from binary precision/recall denominators and report their counts. Do not silently count them as negatives.

## Exact cue taxonomy

| Cue | Present when | Exclude / review |
| --- | --- | --- |
| `direct_identifier` | The ad reveals or addresses the *viewer’s* email, phone or similar direct identifier. | A seller's contact email/phone is `absent`, even though the current regex can match it. Identity ownership unclear: `ambiguous`. |
| `sensitive_personal_fact` | The ad asserts a fact about the viewer's health, finances, religion, sexuality or equivalent sensitive status. | Generic product categories, such as skin care, do not assert a viewer fact. |
| `explicit_surveillance` | The advertiser says it tracks, watches or knows the viewer's activity. | A denial of tracking is absent; quoted/disclosed text needs scope review. |
| `precise_location` | The ad asserts the viewer's home, address, exact position or current whereabouts. | Generic delivery area is absent. |
| `approximate_location` | The ad asserts an inferred city, area or nearby location *of the viewer*. | “Delivery across the city” without personal inference is absent. |
| `browsing_history` | The ad refers to the viewer's search, site visit or browsing trail. | Generic product interest is absent; implication without an explicit trail is ambiguous. |
| `purchase_history` | The ad invokes the viewer's earlier order, purchase or cart. | A generic “buy” offer is absent. |
| `interest_targeting` | The ad says it used the viewer's expressed or inferred interests. | “You will love this” alone is ambiguous at most. |
| `personalized_claim` | The ad explicitly claims a tailored/selected/recommended offer *for the viewer*. | A general recommendation or age suitability is absent. |
| `combined_signals` | At least two distinct asserted personal-data signal categories above coexist. | Derived only from present labels. |
| `specific_activity_detail` | An asserted browsing-history cue has a specific time/activity detail. | A standalone date or product description is absent. |
| `no_consent` | Copy explicitly states data use without permission. | A consent assurance is absent; actual legal validity is outside this screen. |
| `broad_targeting` | Supplied targeting settings explicitly declare broad age/city/country/interest selection. | Ad copy alone cannot establish a campaign setting; unassessable without targeting input. |
| `countdown_pressure` | A visible timer or countdown urges a time-limited action. | A mere date, price or time display without countdown is absent. |
| `scarcity_claim` | Stock/quantity is said to be limited or almost gone. | Figurative seasonal “vanish” wording is ambiguous without a concrete stock claim. |
| `extreme_discount` | An explicit **80%–100% off** discount appears. | “100% pure” and 75% off are absent. No conversion from multi-buy to an implied percent. |
| `urgent_call_to_action` | Explicit temporal pressure such as “last chance”, “limited time only/offer”, “today only”, or a command linked to a deadline. | “Shop now” or “order now” without a deadline is an ordinary CTA and absent. |
| `alarmist_claim` | A threatening, fearful or conspiratorial consequence is asserted to drive action. | Playful “warning” for perfume or “beware the heat” for sauce is absent. |
| `excessive_exclamation` | Two or more emphatic runs of three or more exclamation marks appear. | One exclamation point is absent. |

Negation scope, quotations, sarcasm, rhetorical questions and disclosures must be read in context. A quoted *actual promotional headline* remains a cue; a quoted example of what **not** to say is absent. A disclosure of tracking can be present as a wording cue without establishing that tracking occurs. When an image has text beyond the source CSV, label that image separately; do not assume the CSV is a perfect transcription. Image objects, obstruction and hidden tracking are outside this codebook.

## Phase 12 annotation protocol

The AI assistant made one project-authored interpretation pass over source CSV text and inspected selected source screenshots; no current regex outputs or model scores were used to set labels. The frozen labels are in `phase12_validation/real_ad_labels_v1.json` and source content is identified by publisher row and SHA-256 hashes. These are **AI-assisted project-authored Tier B labels, not independent human annotations**. The publisher's annotators rated different properties; no Tier C independent cue labels or inter-rater agreement are claimed. Cases with mixed Arabic copy are kept as an assessability audit and excluded from English-only binary estimates unless an English cue is explicit and the other-language content is independently assessed. Frozen `development` and `test` creative IDs must never be moved after evaluation. Rule changes, if any, can use development only; run final test once. Near-duplicate images and copied text must stay in one partition or be excluded.
