from __future__ import annotations

from typing import List


BASIC_CBT_STRATEGIES = {
    "anxious": [
        "Box breathing (inhale 4, hold 4, exhale 4, hold 4) for 2 minutes",
        "List your top 3 worries, then write one small action for each",
        "Identify thinking traps (catastrophizing, mind-reading) and reframe"
    ],
    "sad": [
        "Do a 10-minute activation task (stretch, short walk, light chore)",
        "Text a supportive friend to check in",
        "Write three small things you can control today"
    ],
    "angry": [
        "Step away and do paced breathing (inhale 4, exhale 6)",
        "Label the emotion intensity 1-10 and re-evaluate after 5 minutes",
        "Write needs and boundaries clearly before responding"
    ],
    "overwhelmed": [
        "Use a 10-3-1 list: 10 minute task, 3 minute task, 1 minute task",
        "Try the 5-4-3-2-1 grounding exercise",
        "Break tasks into two-minute actions and start the easiest"
    ],
}


def suggest_strategies(mood: str) -> List[str]:
    mood_norm = mood.strip().lower()
    if mood_norm in BASIC_CBT_STRATEGIES:
        return BASIC_CBT_STRATEGIES[mood_norm]
    return [
        "Take two slow breaths and unclench your jaw",
        "Name the emotion and rate intensity 1-10",
        "Pick one small action you can do in 2 minutes",
    ]
