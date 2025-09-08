
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Any, List

ABUSIVE_WORDS = {
    "idiot","stupid","nonsense","fool","dumb","shut up","bloody","moron","bastard",
    "jerk","trash","loser","scam","fraudster","screw you","kill yourself"
}
SPAM_HINTS = {
    "http","www","bit.ly","tinyurl","offer","free","limited time","click here","earn money",
    "guaranteed","promo","discount code","subscribe","join now","invest now"
}

# Regex for Indian mobile numbers (e.g., +91 9876543210, 98765-43210, 9876543210)
PHONE_REGEXES = [
    re.compile(r"(?:\+?91[-\s]*)?[6-9]\d{4}[-\s]*\d{5}"),
    re.compile(r"(?:\+?91[-\s]*)?\(?[6-9]\d{2}\)?[-\s]*\d{3}[-\s]*\d{4}"),
]

@dataclass
class ModerationResult:
    label: str                # "safe" | "abusive" | "spam" | "contains_phone"
    reasons: List[str]
    spans: List[Dict[str, Any]]

def _find_phone_spans(text: str) -> List[Dict[str, Any]]:
    spans = []
    for rx in PHONE_REGEXES:
        for m in rx.finditer(text):
            spans.append({"type": "phone", "start": m.start(), "end": m.end(), "match": m.group()})
    return spans

def _find_abuse_spans(text: str) -> List[Dict[str, Any]]:
    spans = []
    low = text.lower()
    for w in ABUSIVE_WORDS:
        start = 0
        while True:
            idx = low.find(w, start)
            if idx == -1:
                break
            spans.append({"type": "abusive", "start": idx, "end": idx+len(w), "match": text[idx:idx+len(w)]})
            start = idx + len(w)
    return spans

def _is_spammy(text: str) -> List[Dict[str, Any]]:
    spans = []
    low = text.lower()
    # heuristic triggers
    for hint in SPAM_HINTS:
        start = 0
        while True:
            idx = low.find(hint, start)
            if idx == -1:
                break
            spans.append({"type": "spam_hint", "start": idx, "end": idx+len(hint), "match": text[idx:idx+len(hint)]})
            start = idx + len(hint)
    # excessive digits
    for m in re.finditer(r"\d{5,}", text):
        spans.append({"type": "digits", "start": m.start(), "end": m.end(), "match": m.group()})
    # repeated characters (e.g., !!!!!, $$$$$)
    for m in re.finditer(r"([!$#%*?~])\1{3,}", text):
        spans.append({"type": "repeated_punct", "start": m.start(), "end": m.end(), "match": m.group()})
    return spans

@dataclass
class ChatModerator:
    def moderate(self, message: str) -> Dict[str, Any]:
        reasons: List[str] = []
        spans: List[Dict[str, Any]] = []

        phone_spans = _find_phone_spans(message)
        if phone_spans:
            spans.extend(phone_spans)
            reasons.append("contains a phone number")

        abuse_spans = _find_abuse_spans(message)
        if abuse_spans:
            spans.extend(abuse_spans)
            reasons.append("contains abusive language")

        spam_spans = _is_spammy(message)
        # Mark spam only if spam hints are prominent and not just numbers that are part of pricing
        # (heuristic: at least one link/marketing cue OR >15 total digits outside a single number)
        link_or_marketing = any(s["type"] in {"spam_hint"} for s in spam_spans)
        many_digits = sum(len(s["match"]) for s in spam_spans if s["type"] == "digits") >= 15
        if link_or_marketing or many_digits:
            # avoid falsely classifying a normal price quote as spam
            spans.extend(spam_spans)
            reasons.append("spam-like content")

        # Priority: abusive > spam > contains_phone > safe
        if abuse_spans:
            label = "abusive"
        elif (link_or_marketing or many_digits):
            label = "spam"
        elif phone_spans:
            label = "contains_phone"
        else:
            label = "safe"
            if not reasons:
                reasons.append("no policy violations detected")

        return {"label": label, "reasons": reasons, "spans": spans}
