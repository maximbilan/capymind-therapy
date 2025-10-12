from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path.home() / ".capymind_session"
MOOD_FILE = DATA_DIR / "mood.ndjson"


@dataclass
class MoodLog:
    timestamp_iso: str
    mood: str
    intensity: int  # 1-10


VALID_MOODS = {
    "calm",
    "happy",
    "content",
    "sad",
    "anxious",
    "angry",
    "overwhelmed",
    "lonely",
    "stressed",
    "tired",
}


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def log_mood(mood: str, intensity: int) -> MoodLog:
    ensure_data_dir()
    mood_norm = mood.strip().lower()
    if not (1 <= intensity <= 10):
        raise ValueError("intensity must be between 1 and 10")
    entry = MoodLog(
        timestamp_iso=datetime.utcnow().isoformat() + "Z",
        mood=mood_norm,
        intensity=intensity,
    )
    MOOD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MOOD_FILE.open("a", encoding="utf-8") as f:
        f.write(
            f"{{\"timestamp_iso\": \"{entry.timestamp_iso}\", \"mood\": \"{entry.mood}\", \"intensity\": {entry.intensity}}}\n"
        )
    return entry


def mood_summary(limit: int = 20) -> Dict[str, float]:
    ensure_data_dir()
    if not MOOD_FILE.exists():
        return {}
    lines = MOOD_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
    import json
    totals: Dict[str, int] = {}
    counts: Dict[str, int] = {}
    for line in lines:
        try:
            obj = json.loads(line)
            m = obj["mood"]
            totals[m] = totals.get(m, 0) + obj["intensity"]
            counts[m] = counts.get(m, 0) + 1
        except Exception:
            continue
    return {mood: totals[mood] / counts[mood] for mood in counts}
