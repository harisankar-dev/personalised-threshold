"""Three-tier ad intrusion-risk screen for text or OCR-extracted image copy.

This is a transparent, unvalidated proxy model. The source CSVs do not have
perceived-intrusiveness labels, so these tiers are not learned consumer ratings.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from threshold_engine import current_dataset_status


ROOT = Path(__file__).resolve().parent
MODEL_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

# A cue contributes at most once, even if different phrases express it. The
# weights are an explicit design rubric, not fitted coefficients or survey means.
COPY_CUES = [
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
    ("urgent_call_to_action", 2, re.compile(r"\b(?:last chance|today only|click (?:the )?link now|act now|hurry|before the timer runs out|limited[ -]time (?:offers?|deals?|sale)|(?:offer|sale|deal) ends? (?:tonight|tomorrow|today|at midnight|on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))|this weekend only|final day|(?:offer|sale|deal) valid until (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tonight|tomorrow)|ends? at midnight|\d{1,2}[ -]hour special|only until (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tonight|tomorrow)|last day to claim)\b", re.I)),
    ("alarmist_claim", 2, re.compile(r"\b(?:they do not want you to see|we get taken down|taken down|alert!{2,})\b", re.I)),
]
EXCESSIVE_EXCLAMATION_PATTERN = re.compile(r"!{3,}")
IDENTIFIER_VALUE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|(?<!\w)(?:\+?\d[\d .()\-]{8,}\d)(?!\w)", re.I)
VIEWER_IDENTIFIER = re.compile(
    r"\b(?:(?:we (?:know|identified|have|found|obtained) your|you(?:'|’)re identified by your)\s*(?:phone(?: number)?|mobile(?: number)?|email(?: address)?|account(?: number)?|home address)\b|your (?:personal|private|own)?\s*(?:phone(?: number)?|mobile(?: number)?|email(?: address)?|account(?: number)?|home address)\s*(?:is\b|was\b|[:=]))", re.I)
SELLER_CONTEXT = re.compile(r"\b(?:call|contact|email|whatsapp|text|reach|apply|support|careers?|recruitment|customer service|helpdesk|order|book|visit|showroom|our|us|designed by|example|e\.g\.)\b", re.I)
EXAMPLE_CONTEXT = re.compile(r"\b(?:for example|example|sample|placeholder|the phrase|avoid saying|do not say|don't say)\b", re.I)
META_QUOTE = re.compile(r"\b(?:the phrase|avoid saying|do not say|don(?:'|’)t say|is misleading|means|quoted example)\b", re.I)
DENIAL_BEFORE_CUE = re.compile(
    r"(?:\b(?:do\s+not|don(?:'|’)t|never|not)\s+(?:use|using|say|said|claim|write|track|record|rely\s+on)\b[^.;!?]{0,30}?|"
    r"\bnot\s+|\bnever\s+said\s+)[\s'\"“”‘’]*$", re.I)

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
    "direct_identifier": "Remove claims that identify the viewer by phone, email, account or home address; use a general offer instead.",
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


def _asserted_match(pattern: re.Pattern[str], content: str) -> re.Match[str] | None:
    """Skip a cue when a local explicit denial scopes over its phrase.

    This is a narrow syntax guard, not full natural-language understanding.
    A later positive mention in another clause can still be detected.
    """
    for match in pattern.finditer(content):
        prefix = content[max(0, match.start() - 65):match.start()]
        prefix = re.split(r"[.;!?\n]", prefix)[-1]
        suffix = content[match.end():min(len(content), match.end() + 35)]
        quoted_meta = bool(META_QUOTE.search(prefix + suffix)) and not bool(re.search(r"\bour headline is\b", prefix, re.I))
        if not DENIAL_BEFORE_CUE.search(prefix) and not quoted_meta:
            return match
    return None


def identifier_evidence(text: str) -> tuple[dict | None, list[str]]:
    """Score explicit viewer ownership; keep bare contacts as ownership-uncertain."""
    warnings = []
    claim = _asserted_match(VIEWER_IDENTIFIER, text)
    if claim:
        prefix = text[max(0, claim.start() - 45):claim.start()]
        suffix = text[claim.end():min(len(text), claim.end() + 55)]
        if not EXAMPLE_CONTEXT.search(prefix) and not re.search(r"\bis (?:an? )?(?:example|sample|placeholder)\b", suffix, re.I):
            return {"cue": "direct_identifier", "source": "ad_copy",
                    "matched": claim.group(0), "weight": 6}, warnings
    for match in IDENTIFIER_VALUE.finditer(text):
        clause = re.split(r"[.;!?\n]", text[max(0, match.start() - 90):match.start()])[-1]
        around = clause + text[match.end():min(len(text), match.end() + 45)]
        if EXAMPLE_CONTEXT.search(around) or SELLER_CONTEXT.search(around):
            continue
        warnings.append("A contact detail was found, but its owner is unclear. Review it before treating it as viewer-specific.")
        break
    return None, warnings


def classify(text: str, targeting: str = "") -> dict:
    if not text.strip() and not targeting.strip():
        return {"tier": "needs_review", "score": None, "score_out_of_10": None,
                "privacy_score": None, "pressure_score": None, "evidence": [], "recommendations": [],
                "reason": "No readable ad copy or targeting information was available."}
    found = {}
    identifier, review_flags = identifier_evidence(text)
    if identifier:
        found["direct_identifier"] = identifier
    for source, rules, content in [("ad_copy", COPY_CUES, text), ("targeting", TARGETING_CUES, targeting)]:
        for name, weight, pattern in rules:
            match = _asserted_match(pattern, content)
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
        match = _asserted_match(pattern, text)
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
    if review_flags and score == 0:
        tier = "needs_review"
        score = None
    if review_flags:
        note += " " + " ".join(review_flags)
    return {"tier": tier, "score": score, "score_out_of_10": min(10, score) if score is not None else None,
            "privacy_score": privacy_score, "pressure_score": pressure_score, "evidence": evidence,
            "recommendations": suggest_repairs(evidence),
            "reason": note, "review_flags": review_flags}


def ocr_image(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    def recognize(image: Path, psm: str | None = None) -> dict:
        cmd = ["node", str(ROOT / "ocr_ad.cjs"), str(image)]
        if psm:
            cmd.append(psm)
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=45)
        if proc.returncode:
            raise RuntimeError(proc.stderr.strip() or "OCR failed")
        return json.loads(proc.stdout)

    first = recognize(path)
    first_text = first["text"].strip()
    if first["confidence"] > 65 and len(re.findall(r"[A-Za-z]{3,}", first_text)) >= 4:
        return {**first, "passes": 1, "quality_warning": None}
    # A single bounded second pass is preferable to indiscriminate transforms.
    scratch = ROOT / ".ocr_tmp"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as temporary:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
            factor = min(2.0, 1600 / max(image.size))
            if abs(factor - 1.0) > 0.01:
                image = image.resize((max(1, round(image.width * factor)),
                                      max(1, round(image.height * factor))), Image.Resampling.LANCZOS)
            image = ImageOps.grayscale(image)
            image = ImageOps.autocontrast(image, cutoff=1)
            image = ImageEnhance.Contrast(image).enhance(1.4)
            enhanced = Path(temporary) / "enhanced.png"
            image.save(enhanced)
        second = recognize(enhanced, "11")
    lines = []
    seen = set()
    for transcript in (first_text, second["text"]):
        for line in transcript.splitlines():
            line = re.sub(r"\s+", " ", line).strip()
            key = re.sub(r"[^a-z0-9]+", "", line.lower())
            if key and key not in seen:
                seen.add(key)
                lines.append(line)
    merged = "\n".join(lines)[:5000]
    severe = (max(first["confidence"], second["confidence"]) < 35 and len(merged) > 800)
    warning = ("OCR is severely garbled; review the image manually."
               if severe else "OCR may be partial; check visible text against the image.")
    return {"text": merged, "confidence": first["confidence"],
            "enhanced_confidence": second["confidence"], "passes": 2,
            "quality_warning": warning, "severely_garbled": severe}


def predict(text: str = "", image: Path | None = None, targeting: str = "", visual_description: str = "") -> dict:
    ocr = None
    if image is not None:
        ocr = ocr_image(image)
    ad_copy = " ".join(x for x in [text, ocr["text"] if ocr else "", visual_description] if x)
    result = classify(ad_copy, targeting)
    result.update({"input_text": text, "image": str(image) if image else None,
                   "ocr_text": ocr["text"] if ocr else None,
                   "ocr_confidence": ocr["confidence"] if ocr else None,
                   "ocr_warning": ocr.get("quality_warning") if ocr else None,
                   "ocr_passes": ocr.get("passes") if ocr else None,
                   "visual_objects_assessed": False if image else None,
                   "visual_description": visual_description or None,
                   "targeting": targeting or None})
    result["threshold_decision"] = current_dataset_status()
    result["model_version"] = MODEL_VERSION
    if image:
        result["reason"] += " Image objects and scenes were not assessed; OCR reads printed text only."
        if ocr.get("quality_warning"):
            result["reason"] += " " + ocr["quality_warning"]
        if ocr.get("severely_garbled") and not text.strip() and not visual_description.strip():
            result["tier"] = "needs_review"
            result["score"] = None
            result["score_out_of_10"] = None
            result["reason"] = "OCR was severely garbled. Review the image manually before assigning a creative cue tier."
    if image and result["score"] == 0:
        # A zero OCR cue count cannot establish that a visual ad is low-risk.
        result["tier"] = "needs_review"
        result["score"] = None
        result["score_out_of_10"] = None
        result["reason"] = "No matching cues in the OCR text. Visual content is unassessed, so this image needs review rather than a low-risk conclusion."
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
