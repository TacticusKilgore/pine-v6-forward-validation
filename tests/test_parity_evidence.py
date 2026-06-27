from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reports.parity_evidence import (
    build_parity_evidence_report,
    write_parity_evidence_json,
    write_parity_evidence_markdown,
)


def write_export(path: Path, *, long_values: list[int], short_values: list[int]) -> None:
    pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z", "2026-01-01T00:05:00Z", "2026-01-01T00:10:00Z"],
            "EXP_longSignal": long_values,
            "EXP_shortSignal": short_values,
            "EXP_state": ["Neutral", "Active Long", "Neutral"],
            "EXP_score": [0.0, 75.0, 0.0],
        }
    ).to_csv(path, index=False)


def test_matching_parity_evidence_passes(tmp_path: Path) -> None:
    pine = tmp_path / "pine.csv"
    py = tmp_path / "python.csv"
    write_export(pine, long_values=[0, 1, 0], short_values=[0, 0, 0])
    write_export(py, long_values=[0, 1, 0], short_values=[0, 0, 0])
    report = build_parity_evidence_report(
        pine_export_path="pine.csv",
        python_output_path="python.csv",
        strategy="amlrx",
        symbol="BTCUSDT",
        timeframe="5m",
        root=tmp_path,
    )
    assert report.passed
    assert report.severity == "GO"
    assert report.checked_rows == 3
    assert report.signal_bar_match_rate == 1.0
    assert report.direction_match_rate == 1.0


def test_direction_mismatch_holds(tmp_path: Path) -> None:
    pine = tmp_path / "pine.csv"
    py = tmp_path / "python.csv"
    write_export(pine, long_values=[0, 1, 0], short_values=[0, 0, 0])
    write_export(py, long_values=[0, 0, 0], short_values=[0, 1, 0])
    report = build_parity_evidence_report(
        pine_export_path="pine.csv",
        python_output_path="python.csv",
        strategy="amlrx",
        symbol="BTCUSDT",
        timeframe="5m",
        root=tmp_path,
    )
    assert not report.passed
    assert report.severity == "HOLD"
    assert report.critical_mismatches > 0
    assert report.direction_match_rate == 0.0


def test_missing_file_holds(tmp_path: Path) -> None:
    report = build_parity_evidence_report(
        pine_export_path="missing_pine.csv",
        python_output_path="missing_python.csv",
        strategy="iax",
        symbol="ETHUSDT",
        timeframe="5m",
        root=tmp_path,
    )
    assert not report.passed
    assert report.severity == "HOLD"
    assert report.critical_mismatches == 1


def test_write_parity_evidence_reports(tmp_path: Path) -> None:
    pine = tmp_path / "pine.csv"
    py = tmp_path / "python.csv"
    write_export(pine, long_values=[0, 1, 0], short_values=[0, 0, 0])
    write_export(py, long_values=[0, 1, 0], short_values=[0, 0, 0])
    report = build_parity_evidence_report(
        pine_export_path="pine.csv",
        python_output_path="python.csv",
        strategy="amlrx",
        symbol="BTCUSDT",
        timeframe="5m",
        root=tmp_path,
    )
    json_out = write_parity_evidence_json(report, tmp_path / "report.json")
    md_out = write_parity_evidence_markdown(report, tmp_path / "report.md")
    assert json_out.is_file()
    assert md_out.is_file()
    assert "Real Parity Evidence Report" in md_out.read_text(encoding="utf-8")
