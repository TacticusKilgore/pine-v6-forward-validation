from __future__ import annotations

from typing import Any

from .models import ForwardEvent


def normalize_event(event: ForwardEvent) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "correlation_id": event.correlation_id,
        "run_id": event.run_id,
        "build_id": event.build_id,
        "event_type": event.event_type,
        "event_time_utc": event.event_time_utc,
        "bar_time_utc": event.bar_time_utc,
        "symbol": event.symbol,
        "timeframe": event.timeframe,
        "direction": event.direction,
        "sequence": event.sequence,
    }
    for key, value in event.payload.items():
        record[f"payload_{key}"] = value
    return record
