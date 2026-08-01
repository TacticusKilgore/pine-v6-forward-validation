from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import ForwardEvent


class SQLiteDedupeStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS events "
                "(event_id TEXT PRIMARY KEY, received_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def claim(self, event_id: str) -> bool:
        try:
            with sqlite3.connect(self.path) as conn:
                conn.execute("INSERT INTO events(event_id) VALUES (?)", (event_id,))
            return True
        except sqlite3.IntegrityError:
            return False


class JsonlRawStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: ForwardEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"
            )

    def read(self) -> Iterable[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
