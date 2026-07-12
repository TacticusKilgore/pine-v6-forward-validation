from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA_VERSION = "FTL_V2"
EVENT_TYPES = {
    "CONFIG_START", "HEARTBEAT", "SIGNAL_CANDIDATE", "SIGNAL_VALID",
    "SIGNAL_BLOCKED", "ENTRY_INTENT", "ORDER_FILLED", "INVALIDATION",
    "TARGET_HIT", "EXIT", "SIGNAL_EXPIRED", "RUNTIME_ERROR",
}
DIRECTIONS = {"LONG", "SHORT", "NONE"}


class EventValidationError(ValueError):
    pass


def _parse_utc(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise EventValidationError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise EventValidationError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ForwardEvent:
    schema_version: str
    event_id: str
    correlation_id: str
    run_id: str
    build_id: str
    event_type: str
    event_time_utc: str
    bar_time_utc: str
    symbol: str
    timeframe: str
    direction: str = "NONE"
    sequence: int = 0
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ForwardEvent":
        required = (
            "schema_version", "event_id", "correlation_id", "run_id", "build_id",
            "event_type", "event_time_utc", "bar_time_utc", "symbol", "timeframe",
        )
        missing = [key for key in required if value.get(key) in (None, "")]
        if missing:
            raise EventValidationError(f"missing required fields: {missing}")
        event = cls(
            schema_version=str(value["schema_version"]),
            event_id=str(value["event_id"]),
            correlation_id=str(value["correlation_id"]),
            run_id=str(value["run_id"]),
            build_id=str(value["build_id"]),
            event_type=str(value["event_type"]).upper(),
            event_time_utc=str(value["event_time_utc"]),
            bar_time_utc=str(value["bar_time_utc"]),
            symbol=str(value["symbol"]),
            timeframe=str(value["timeframe"]),
            direction=str(value.get("direction", "NONE")).upper(),
            sequence=int(value.get("sequence", 0)),
            payload=dict(value.get("payload") or {}),
        )
        event.validate()
        return event

    def validate(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise EventValidationError(f"unsupported schema_version: {self.schema_version}")
        if self.event_type not in EVENT_TYPES:
            raise EventValidationError(f"unsupported event_type: {self.event_type}")
        if self.direction not in DIRECTIONS:
            raise EventValidationError(f"unsupported direction: {self.direction}")
        if len(self.event_id) < 16 or len(self.correlation_id) < 8:
            raise EventValidationError("event_id/correlation_id too short")
        if self.sequence < 0:
            raise EventValidationError("sequence must be non-negative")
        _parse_utc(self.event_time_utc, "event_time_utc")
        _parse_utc(self.bar_time_utc, "bar_time_utc")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
