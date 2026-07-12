from __future__ import annotations

import hashlib


def deterministic_event_id(
    *,
    run_id: str,
    build_id: str,
    symbol: str,
    timeframe: str,
    bar_time_utc: str,
    event_type: str,
    direction: str,
    sequence: int = 0,
) -> str:
    material = "|".join(
        [
            run_id,
            build_id,
            symbol,
            timeframe,
            bar_time_utc,
            event_type.upper(),
            direction.upper(),
            str(sequence),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
