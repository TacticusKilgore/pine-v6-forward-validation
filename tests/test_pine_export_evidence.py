from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reports.pine_export_evidence import (
    build_pine_export_evidence_report,
    write_pine_export_evidence_json,
    write_pine_export_evidence_markdown,
)


def manifest(path: str = "data/pine_exports/amlrx/BTCUSDT/5m/export.csv") -> dict:
    return {
        "pine_exports": {
            "amlrx": {
                "BTCUSDT": {
                    "5m": [path],
                }
            }
        }
    }


def test_declared_export_passes_without_file_check() -> None:
    report = build_pine_export_evidence_report(manifest(), require_existing_files=False)
    assert report.passed
    assert report.rows[0].severity == "DECLARED"
    assert report.to_dict()["summary"]["declared_only"] == 1


def test_missing_export_fails_when_file_required(tmp_path: Path) -> None:
    report = build_pine_export_evidence_report(manifest(), root=tmp_path, require_existing_files=True)
    assert not report.passed
    assert report.rows[0].severity == "ERROR"


def test_existing_export_with_required_columns_passes(tmp_path: Path) -> None:
    export_path = tmp_path / "export.csv"
    pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z"],
            "EXP_longSignal": [1],
            "EXP_shortSignal": [0],
            "EXP_state": ["Active Long"],
            "EXP_score": [75.0],
        }
    ).to_csv(export_path, index=False)
    report = build_pine_export_evidence_report(manifest("export.csv"), root=tmp_path, require_existing_files=True)
    assert report.passed
    assert report.rows[0].severity == "OK"
    assert report.rows[0].rows == 1


def test_existing_export_missing_required_columns_fails(tmp_path: Path) -> None:
    export_path = tmp_path / "export.csv"
    pd.DataFrame({"timestamp": ["2026-01-01T00:00:00Z"], "EXP_longSignal": [1]}).to_csv(export_path, index=False)
    report = build_pine_export_evidence_report(manifest("export.csv"), root=tmp_path, require_existing_files=True)
    assert not report.passed
    assert report.rows[0].severity == "ERROR"
    assert "EXP_shortSignal" in report.rows[0].missing_required_columns


def test_write_reports(tmp_path: Path) -> None:
    report = build_pine_export_evidence_report(manifest(), require_existing_files=False)
    json_out = write_pine_export_evidence_json(report, tmp_path / "report.json")
    md_out = write_pine_export_evidence_markdown(report, tmp_path / "report.md")
    assert json_out.is_file()
    assert md_out.is_file()
    assert "Pine Export Evidence Report" in md_out.read_text(encoding="utf-8")
