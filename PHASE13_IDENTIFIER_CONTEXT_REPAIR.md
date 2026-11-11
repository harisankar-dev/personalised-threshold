# Phase 13 seller versus viewer identifier repair

The Phase 12 rubric matched any phone number or email address as a 6-point `direct_identifier` cue. That converted advertiser contact information into an apparent viewer-specific privacy alarm. A real delivery ad's public phone produced a false high image alert; a recruitment email was also misread in text.

`intrusive_ad_model.py` now removes the bare identifier regex from scored copy cues. It scores explicit ownership language such as “We know your phone number,” “Your personal email is…,” “We identified your account,” and “We know your home address.” Contact values with nearby call, order, support, careers, WhatsApp, showroom, “our” or other seller context are not scored as viewer identity. A bare contact value whose owner cannot be resolved returns `needs_review`, no numeric score, and an explicit ownership warning unless other independent cues are present. Quoted examples and local denials are guarded. The six-point weight and tier boundaries did not change.

| Example | Phase 12 behaviour | Phase 13 behaviour |
| --- | --- | --- |
| “Call 9876543210 to order.” | High 6/10 from number alone | No viewer identifier cue |
| “Email careers@example.com to apply.” | High 6/10 from email alone | No viewer identifier cue |
| “We know your phone number.” | No literal number, often missed | High 6/10 explicit viewer claim |
| “Your personal email is alice@example.com.” | High via raw email | High via viewer ownership |
| Unowned bare email | High via raw email | Review with no numeric score |

The fresh real-ad ID 538 contains a seller email. On visually checked phrase text and the image pipeline, the Phase 12 screen produced one false `direct_identifier`; the revised screen produced zero. The other four assessable reserved-test images did not contain an identity positive. This is a narrow false-positive correction, **not** measured recall for real viewer-specific ads. Synthetic tests cover seller phone/email/support/recruitment/example, quoted and negated cases, and explicit viewer claims. Chrome uploads of real seller-phone ID 389 and seller-email ID 538 showed no direct-identifier alert; a text viewer claim did alert.

Ownership can still be ambiguous in short, fragmented or badly OCR'd copy. Context matching is local regex logic, not entity resolution. A genuinely viewer-owned contact shown without an explicit referent may be sent to review rather than scored high. Conversely, complex prose could still misassign ownership. Independent real positives are needed before claiming robust privacy-cue performance.
