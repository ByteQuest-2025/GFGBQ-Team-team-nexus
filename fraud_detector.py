import re
from typing import List, Dict

from utils import clean_text

# Rule definitions: keywords are matched with word boundaries (case-insensitive).
# Each rule has a human-readable reason and a score contribution.
RULES = [
    {
        "name": "OTP request",
        "reason": "OTP request detected",
        "keywords": ["otp", "one time password", "pin", "passcode"],
        "score": 30,
    },
    {
        "name": "Bank impersonation",
        "reason": "Bank impersonation",
        "keywords": ["bank", "rbi", "reserve bank", "customer care", "account"],
        "score": 25,
    },
    {
        "name": "Urgency",
        "reason": "Urgency language detected",
        "keywords": ["immediately", "urgent", "last chance", "abhi", "right now", "asap"],
        "score": 20,
    },
    {
        "name": "Threat/Fear",
        "reason": "Threat or fear language detected",
        "keywords": ["freeze", "blocked", "suspended", "legal action", "lawsuit", "police", "arrest"],
        "score": 15,
    },
    {
        "name": "Financial trigger",
        "reason": "Financial trigger detected",
        "keywords": ["upi", "transfer", "account number", "ifsc", "verify", "pay now"],
        "score": 10,
    },
]


def analyze_transcript(transcript: str, segments: List[Dict] = None) -> Dict:
    """Analyze transcript and optional segments to produce score, level, reasons.

    Returns dict with keys: score (0-100), level (LOW/MEDIUM/HIGH), reasons (list), timestamps (list)
    """
    text = transcript or ""
    text_clean = clean_text(text)

    reasons = []
    score = 0

    # Detect rules in overall transcript
    for rule in RULES:
        for kw in rule["keywords"]:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_clean, re.IGNORECASE):
                if rule["reason"] not in reasons:
                    reasons.append(rule["reason"])
                    score += rule["score"]
                break

    score = min(100, score)

    if score <= 30:
        level = "LOW"
    elif score <= 60:
        level = "MEDIUM"
    else:
        level = "HIGH"

    timestamps = []
    if segments:
        for seg in segments:
            seg_text = seg.get("text", "")
            seg_start = seg.get("start", 0)
            for rule in RULES:
                for kw in rule["keywords"]:
                    pattern = r"\b" + re.escape(kw) + r"\b"
                    if re.search(pattern, seg_text, re.IGNORECASE):
                        timestamps.append({"phrase": kw, "reason": rule["reason"], "start": seg_start})
                        break

    return {"score": score, "level": level, "reasons": reasons, "timestamps": timestamps}
