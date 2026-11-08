"""Three-tier ad intrusion-risk screen for text or OCR-extracted image copy.

This is a transparent, unvalidated proxy model. The source CSVs do not have
perceived-intrusiveness labels, so these tiers are not learned consumer ratings.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# A cue contributes at most once, even if different phrases express it. The
# weights are an explicit design rubric, not fitted coefficients or survey means.
COPY_CUES = [
    ("direct_identifier", 6, re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|\b(?:\+?\d[\d .()\-]{8,}\d)\b", re.I)),
    ("sensitive_personal_fact", 6, re.compile(r"\b(?:your|you have|we know (?:your|about your))\s+(?:diagnosis|medical history|pregnancy|fertility|debt|credit score|income|religion|sexual orientation|mental health|prescription|bank balance)\b", re.I)),
    ("explicit_surveillance", 5, re.compile(r"\b(?:we(?:'|’)ve been keeping track|we (?:are )?(?:tracking|monitoring|watching|tracked|monitored) (?:you|your)|we (?:keep|kept) track of your (?:activity|visits)|keeping track of your activity|we know (?:where you are|what you did|you (?:are|(?:'|’)re) in [A-Z][a-z]+)|we(?:'|’)ve followed your activity)\b", re.I)),
    ("precise_location", 6, re.compile(r"\b(?:near your (?:home|office|current location)|at your (?:address|home)|you are (?:now |currently )?(?:at|near)|we know you(?:'|’)re currently at)\b", re.I)),
    ("approximate_location", 2, re.compile(r"\b(?:available near you|stores? near you|deals? near you|looking for .{0,60}? in [A-Z][a-z]+|(?:your|you(?:'|’)re) (?:in|near) [A-Z][a-z]+|location in [A-Z][a-z]+|(?:we )?(?:also )?know you(?: are|(?:'|’)re)(?: currently)? in [A-Z][a-z]+)\b", re.I)),
    ("browsing_history", 3, re.compile(r"\b(?:we (?:noticed|saw) (?:that )?you(?:'|’)?(?:ve)? (?:were |have been )?(?:searched|searching|browsed|browsing|visited|visiting|viewed|viewing|checking)|we noticed your recent interest|your recent (?:searches|browsing|views|interest)|based on your (?:recent )?(?:.{0,35}? )?(?:searches|browsing|viewing)|you (?:recently |have been |were )?(?:searched for|searching for|browsed|browsing|viewed|viewing|visited|visiting)|you checked several .{0,60}?websites|sites? you visited|your visits to .{0,35}?sites?)\b", re.I)),
    ("purchase_history", 3, re.compile(r"\b(?:your (?:recent|last|previous|past) (?:.{0,30}? )?(?:purchases?|orders?)|previous .{0,30}? purchases?|based on your (?:past|previous|recent|last) (?:purchase|order)|you (?:bought|purchased)|your (?:shopping )?cart|left .{0,50}? in your cart)\b", re.I)),
    ("interest_targeting", 2, re.compile(r"\b(?:based on your interests?|because you like|you told us you like)\b", re.I)),
    ("personalized_claim", 1, re.compile(r"\b(?:(?:personalized|tailored)\s+(?:collection|plan|experience|for you|to you|recommendations?|offers?)|(?:selected|recommended) (?:just )?for you)\b", re.I)),
]

# Pressure tactics are scored separately from privacy cues so a marketer can
# see why a non-personalized but aggressive creative received a high score.
PRESSURE_CUES = [
    ("countdown_pressure", 3, re.compile(r"\b\d{1,2}\s*:\s*\d{2}\s*:\s*\d{2}(?:\s*:\s*\d{2})?\b|\b(?:timer|countdown)\s+(?:runs?\s+out|ends?|expires?)\b", re.I)),
    ("scarcity_claim", 2, re.compile(r"\b(?:limited stock|only\s+\d+\s+(?:left|remaining)|while stocks last|selling out)\b", re.I)),
    ("extreme_discount", 2, re.compile(r"\b(?:8\d|9\d|100)\s*%\s*off\b", re.I)),
    ("urgent_call_to_action", 2, re.compile(r"\b(?:last chance|today only|click (?:the )?link now|act now|hurry|before the timer runs out)\b", re.I)),
    ("alarmist_claim", 2, re.compile(r"\b(?:they do not want you to see|we get taken down|taken down|alert!{2,})\b", re.I)),
]
EXCESSIVE_EXCLAMATION_PATTERN = re.compile(r"!{3,}")

TARGETING_CUES = [
    ("sensitive_personal_fact", 6, re.compile(r"\b(?:health condition|medical history|pregnancy|religion|credit score|financial hardship)\b", re.I)),
    ("browsing_history", 3, re.compile(r"\b(?:browsing|search history|retargeting|website visits?)\b", re.I)),
    ("purchase_history", 3, re.compile(r"\b(?:purchase history|past purchases|cart abandon)\b", re.I)),
    ("precise_location", 6, re.compile(r"\b(?:gps|precise location|real.time location|home address)\b", re.I)),
    ("approximate_location", 2, re.compile(r"\b(?:approximate location|current city|current region)\b", re.I)),
    ("broad_targeting", 1, re.compile(r"\b(?:age|country|city|region|interest)\s*[:=]", re.I)),
]

DETAIL_PATTERN = re.compile(r"\b(?:last night|yesterday|compared prices|left without buying|didn(?:'|’)t purchase|did not purchase|several .{0,30}? websites)\b", re.I)
NO_CONSENT_PATTERN = re.compile(r"\b(?:without (?:your )?(?:consent|permission)|you (?:did not|didn(?:'|’)t|haven(?:'|’)t) (?:agree|consent)|consent\s*[:=]\s*(?:no|false)|not knowingly agreed)\b", re.I)

# Advice is linked to observed cues. These are editorial proposals, not
# experimentally verified changes in consumer perception.
REPAIR_ADVICE = {
    "direct_identifier": "Remove the email address or phone number from the creative; use a general offer instead.",
    "sensitive_personal_fact": "Remove references to sensitive personal facts and review whether that targeting should be used at all.",
    "explicit_surveillance": "Remove language that says the person was tracked or watched; describe the product benefit directly.",
    "precise_location": "Remove references to the person's home or exact whereabouts; use broad availability wording if location is relevant.",
    "approximate_location": "Use a general regional offer instead of telling the person that their location was observed.",
    "browsing_history": "Avoid revealing observed searches or visited sites; describe the product without naming the browsing trail.",
    "purchase_history": "Avoid calling out a previous order or cart unless that context is expected; lead with the product or offer.",
    "interest_targeting": "Describe the offer without asserting what this person likes or how that preference was learned.",
    "personalized_claim": "Check that the personalization claim reflects an expected, transparent experience.",
    "combined_signals": "Use fewer personal-data signals in the same message; review the revised copy as a whole.",
    "specific_activity_detail": "Remove the timestamp or exact activity detail; keep only information needed to explain the offer.",
    "no_consent": "Do not use this targeting until the consent issue is resolved; revising copy alone is insufficient.",
    "broad_targeting": "Confirm the audience settings match the campaign's stated purpose and expected data use.",
    "countdown_pressure": "Remove the countdown or timer threat; state the actual offer end time plainly if it is verifiable.",
    "scarcity_claim": "Remove the limited-stock claim unless the current quantity is verified and relevant.",
    "extreme_discount": "Check the discount against a genuine reference price and present it without exaggerated graphics or wording.",
    "urgent_call_to_action": "Replace repeated last-chance commands with one clear, optional call to action.",
    "alarmist_claim": "Remove alarm or conspiracy language; describe the offer in a factual tone.",
    "excessive_exclamation": "Reduce repeated exclamation marks and all-caps urgency so the message is easier to assess.",
}


def suggest_repairs(evidence: list[dict]) -> list[dict]:
    return [{"cue": item["cue"], "action": REPAIR_ADVICE[item["cue"]]}
            for item in sorted(evidence, key=lambda item: -item["weight"])
            if item["cue"] in REPAIR_ADVICE]


def classify(text: str, targeting: str = "") -> dict:
    if not text.strip() and not targeting.strip():
        return {"tier": "needs_review", "score": None, "score_out_of_10": None,
                "privacy_score": None, "pressure_score": None, "evidence": [], "recommendations": [],
                "reason": "No readable ad copy or targeting information was available."}
    found = {}
    for source, rules, content in [("ad_copy", COPY_CUES, text), ("targeting", TARGETING_CUES, targeting)]:
        for name, weight, pattern in rules:
            match = pattern.search(content)
            if match and (name not in found or found[name]["weight"] < weight):
                found[name] = {"cue": name, "source": source, "matched": match.group(0), "weight": weight}
    # A generic 'personalized' claim adds no extra risk when a concrete signal
    # already explains the personalization.
    if any(k in found for k in ("browsing_history", "purchase_history", "approximate_location", "precise_location")):
        found.pop("personalized_claim", None)
    evidence = list(found.values())
    signal_types = {k for k in found if k in ("browsing_history", "purchase_history", "approximate_location", "precise_location", "sensitive_personal_fact")}
    if len(signal_types) >= 2:
        evidence.append({"cue": "combined_signals", "source": "derived", "matched": "Multiple personal-data signals", "weight": 1})
    detail = DETAIL_PATTERN.search(text)
    if detail and "browsing_history" in found:
        evidence.append({"cue": "specific_activity_detail", "source": "ad_copy", "matched": detail.group(0), "weight": 1})
    no_consent = NO_CONSENT_PATTERN.search(text + " " + targeting)
    if no_consent:
        evidence.append({"cue": "no_consent", "source": "targeting" if no_consent.start() >= len(text) else "ad_copy", "matched": no_consent.group(0), "weight": 2})
    privacy_score = sum(item["weight"] for item in evidence)
    pressure_evidence = []
    for name, weight, pattern in PRESSURE_CUES:
        match = pattern.search(text)
        if match:
            pressure_evidence.append({"cue": name, "source": "ad_copy", "matched": match.group(0), "weight": weight})
    marks = EXCESSIVE_EXCLAMATION_PATTERN.findall(text)
    if len(marks) >= 2:
        pressure_evidence.append({"cue": "excessive_exclamation", "source": "ad_copy", "matched": "Repeated !!!", "weight": 1})
    pressure_score = sum(item["weight"] for item in pressure_evidence)
    evidence.extend(pressure_evidence)
    score = privacy_score + pressure_score
    tier = "high_intrusive" if score >= 6 else "moderate_intrusive" if score >= 2 else "low_intrusive"
    note = "Rule-based risk estimate; not a measured consumer perception."
    if score > 10:
        note += " Cue points are capped at 10 on the display."
    return {"tier": tier, "score": score, "score_out_of_10": min(10, score),
            "privacy_score": privacy_score, "pressure_score": pressure_score, "evidence": evidence,
            "recommendations": suggest_repairs(evidence),
            "reason": note}


def ocr_image(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    cmd = ["node", str(ROOT / "ocr_ad.cjs"), str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or "OCR failed")
    return json.loads(proc.stdout)


def predict(text: str = "", image: Path | None = None, targeting: str = "", visual_description: str = "") -> dict:
    ocr = None
    if image is not None:
        ocr = ocr_image(image)
    ad_copy = " ".join(x for x in [text, ocr["text"] if ocr else "", visual_description] if x)
    result = classify(ad_copy, targeting)
    result.update({"input_text": text, "image": str(image) if image else None,
                   "ocr_text": ocr["text"] if ocr else None,
                   "ocr_confidence": ocr["confidence"] if ocr else None,
                   "visual_objects_assessed": False if image else None,
                   "visual_description": visual_description or None,
                   "targeting": targeting or None})
    if image:
        result["reason"] += " Image objects and scenes were not assessed; OCR reads printed text only."
    if image and not ocr["text"].strip() and not text.strip() and not visual_description.strip():
        result["tier"] = "needs_review"
        result["score"] = None
        result["score_out_of_10"] = None
        result["privacy_score"] = None
        result["pressure_score"] = None
        result["reason"] = "No readable text found in image. This prototype does not recognize visual objects. Add a visual description for review."
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen ad copy for three intrusion-risk tiers")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Ad text")
    group.add_argument("--image", type=Path, help="Ad image file; English OCR is applied")
    parser.add_argument("--targeting", default="", help="Optional targeting settings used by the marketer")
    parser.add_argument("--visual-description", default="", help="Optional description of non-text image content")
    args = parser.parse_args()
    print(json.dumps(predict(text=args.text or "", image=args.image,
                             targeting=args.targeting, visual_description=args.visual_description),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
