from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bend it all\b",
    r"\boverdose\b",
    r"\bself[- ]?harm\b",
    r"\bcan't go on\b",
    r"\bcan not go on\b",
    r"\bno reason to live\b",
    r"\bwant to die\b",
    r"\bplans? to die\b",
    r"\bimmediate danger\b",
    r"\bemergency\b",
    r"\bassault\b",
    r"\babuse\b",
]


@dataclass
class SafetyCheck:
    is_crisis: bool
    trigger: Optional[str] = None
    level: str = "none"  # none|concern|crisis


def check_crisis(text: str) -> SafetyCheck:
    lowered = text.lower().strip()
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, lowered):
            return SafetyCheck(is_crisis=True, trigger=pattern, level="crisis")
    # Soft concerns
    if any(k in lowered for k in ["hopeless", "worthless", "can't cope", "overwhelmed"]):
        return SafetyCheck(is_crisis=False, trigger=None, level="concern")
    return SafetyCheck(is_crisis=False, trigger=None, level="none")


def crisis_response(location_hint: Optional[str] = None) -> str:
    location_line = (
        "If you are in the United States, you can call or text 988 (Suicide & Crisis Lifeline).\n"
        "In the UK & ROI: Samaritans at 116 123.\n"
        "Canada: Talk Suicide at 1-833-456-4566.\n"
        "Australia: Lifeline at 13 11 14.\n"
        "If elsewhere, please search your local emergency and crisis resources.\n"
    )
    if location_hint:
        location_line = location_hint + "\n" + location_line

    return (
        "I’m really sorry you’re going through this. I’m not a crisis service and I can’t help in emergencies.\n\n"
        "If you are in immediate danger or thinking about harming yourself or someone else, please call your local emergency number right now.\n\n"
        + location_line +
        "You can also reach out to a trusted person near you. When you’re safe, I can continue to listen and support coping conversations."
    )


def safety_disclaimer() -> str:
    return (
        "I’m an AI assistant for general well-being support and education. I’m not a therapist and this is not medical or crisis advice."
    )
