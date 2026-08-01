from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .models import EventValidationError, ForwardEvent
from .normalizer import normalize_event
from .storage import JsonlRawStore, SQLiteDedupeStore


def process_spool(spool_path: str | Path, run_dir: str | Path) -> dict[str, int]:
    spool_path = Path(spool_path)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_store = JsonlRawStore(run_dir / "01_Raw" / "events.jsonl")
    dedupe = SQLiteDedupeStore(run_dir / "05_Audit" / "dedupe.sqlite")
    normalized: list[dict] = []
    failures: list[dict] = []
    if not spool_path.exists():
        return {"accepted": 0, "duplicates": 0, "failed": 0}

    accepted = duplicates = 0
    for line_no, line in enumerate(
        spool_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            event = ForwardEvent.from_mapping(json.loads(line))
            if not dedupe.claim(event.event_id):
                duplicates += 1
                continue
            raw_store.append(event)
            normalized.append(normalize_event(event))
            accepted += 1
        except (json.JSONDecodeError, EventValidationError, TypeError, ValueError) as exc:
            failures.append({"line": line_no, "error": str(exc), "raw": line[:1000]})

    normalized_dir = run_dir / "02_Normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    if normalized:
        pd.DataFrame(normalized).to_csv(normalized_dir / "events.csv", index=False)
    if failures:
        pd.DataFrame(failures).to_csv(normalized_dir / "failures.csv", index=False)
    return {"accepted": accepted, "duplicates": duplicates, "failed": len(failures)}
