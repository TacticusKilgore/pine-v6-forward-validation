from __future__ import annotations

import json

import pandas as pd

from src.forward_logging.ids import deterministic_event_id
from src.forward_logging.models import ForwardEvent
from src.forward_logging.outcomes import resolve_signal_outcomes
from src.forward_logging.worker import process_spool


def sample_event() -> dict:
    event_id = deterministic_event_id(
        run_id="R1",
        build_id="B1",
        symbol="BTCUSDT",
        timeframe="5m",
        bar_time_utc="2026-07-12T00:05:00Z",
        event_type="SIGNAL_VALID",
        direction="LONG",
    )
    return {
        "schema_version": "FTL_V2",
        "event_id": event_id,
        "correlation_id": event_id,
        "run_id": "R1",
        "build_id": "B1",
        "event_type": "SIGNAL_VALID",
        "event_time_utc": "2026-07-12T00:05:01Z",
        "bar_time_utc": "2026-07-12T00:05:00Z",
        "symbol": "BTCUSDT",
        "timeframe": "5m",
        "direction": "LONG",
        "sequence": 0,
        "payload": {"entry_price": 100.0},
    }


def test_event_validates_and_id_is_deterministic() -> None:
    event = ForwardEvent.from_mapping(sample_event())
    assert event.event_type == "SIGNAL_VALID"
    assert event.event_id == sample_event()["event_id"]


def test_outcomes_are_directional_and_future_only() -> None:
    signals = pd.DataFrame(
        [
            {
                "event_id": "e1",
                "bar_time_utc": "2026-01-01T00:00:00Z",
                "direction": "LONG",
                "entry_price": 100.0,
                "invalidation_level": 98.0,
                "target_1": 103.0,
            }
        ]
    )
    candles = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:05:00Z",
                "2026-01-01T00:10:00Z",
                "2026-01-01T00:15:00Z",
            ],
            "open": [100, 100, 101, 102],
            "high": [500, 102, 104, 103],
            "low": [1, 99, 100, 101],
            "close": [100, 101, 103, 102],
        }
    )
    output = resolve_signal_outcomes(signals, candles, horizons=(1, 3))
    assert round(output.loc[0, "return_1_bars"], 4) == 0.01
    assert output.loc[0, "mfe_price"] == 4.0
    assert output.loc[0, "first_touch"] == "TP1"


def test_worker_deduplicates(tmp_path) -> None:
    event = sample_event()
    spool = tmp_path / "spool.jsonl"
    spool.write_text(
        json.dumps(event) + "\n" + json.dumps(event) + "\n",
        encoding="utf-8",
    )
    result = process_spool(spool, tmp_path / "run")
    assert result == {"accepted": 1, "duplicates": 1, "failed": 0}
