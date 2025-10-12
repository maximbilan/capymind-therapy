from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

DATA_DIR = Path.home() / ".capymind_session"
JOURNAL_FILE = DATA_DIR / "journal.ndjson"


@dataclass
class JournalEntry:
    timestamp_iso: str
    text: str


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def add_journal_entry(text: str) -> JournalEntry:
    ensure_data_dir()
    entry = JournalEntry(timestamp_iso=datetime.utcnow().isoformat() + "Z", text=text.strip())
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{{\"timestamp_iso\": \"{entry.timestamp_iso}\", \"text\": {entry.text!r}}}\n")
    return entry


def recent_entries(limit: int = 5) -> List[JournalEntry]:
    ensure_data_dir()
    if not JOURNAL_FILE.exists():
        return []
    lines = JOURNAL_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
    results: List[JournalEntry] = []
    import json

    for line in lines:
        try:
            obj = json.loads(line)
            results.append(JournalEntry(timestamp_iso=obj["timestamp_iso"], text=obj["text"]))
        except Exception:
            continue
    return results
