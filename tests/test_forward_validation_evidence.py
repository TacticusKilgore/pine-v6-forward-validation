from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.reports.forward_validation_evidence import (
    build_forward_validation_evidence_report,
    normalize_forward_frame,
    write_forward_validation_evidence_json,
    write_forward_validation_evidence_markdown,
)


def sample_forward_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=12, freq="5min", tz="UTC"),
            "open": [100.0 + i for i in range(12)],
            "high": [101.0 + i for i in range(12)],
            "low": [99.0 + i for i in range(12)],
            "close": [100.0 + i for i in range(12)],
            "volume": [10.0] * 12,
            "EXP_longSignal": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "EXP_shortSignal": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            "EXP_score": [0, 70, 0, 0, 0, 0, 65, 0, 0, 0, 0, 0],
            "regime": ["trend"] * 6 + ["range"] * 6,
        }
    )


def test_forward_evidence_generates_follow_through() -> None:
    report = build_forward_validation_evidence_report(
        sample_forward_frame(),
        strategy="amlrx",
        symbol="BTCUSDT",
        timeframe="5m",
        horizons=[3, 5, 10],
    )
    assert report.passed
    assert report.checked_rows == 12
    assert report.signal_count == 2
    assert report.side_summary["long"]["3"]["closed"] == 1
    assert report.side_summary["short"]["3"]["closed"] == 1
    assert report.signals[0].results["3"] is not None
    assert report.signals[1].status["10"] == "open"


def test_forward_evidence_detects_unsorted_timestamps() -> None:
    df = sample_forward_frame()
    df.loc[2, "timestamp"] = df.loc[0, "timestamp"] - pd.Timedelta(minutes=5)
    with pytest.raises(ValueError):
        normalize_forward_frame(df)


def test_forward_evidence_detects_duplicate_timestamps() -> None:
    df = sample_forward_frame()
    df.loc[2, "timestamp"] = df.loc[1, "timestamp"]
    with pytest.raises(ValueError):
        normalize_forward_frame(df)


def test_forward_evidence_write_reports(tmp_path: Path) -> None:
    report = build_forward_validation_evidence_report(
        sample_forward_frame(),
        strategy="iax",
        symbol="ETHUSDT",
        timeframe="5m",
        horizons=[3],
    )
    json_out = write_forward_validation_evidence_json(report, tmp_path / "forward.json")
    md_out = write_forward_validation_evidence_markdown(report, tmp_path / "forward.md")
    assert json_out.is_file()
    assert md_out.is_file()
    assert "Forward Validation Evidence Report" in md_out.read_text(encoding="utf-8")
