from __future__ import annotations

from pathlib import Path
import pytest
from src.reports.summary_report import write_summary_report


def test_write_summary_report_creates_file(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    write_summary_report([{"horizon":3,"signals_total":2,"long_signals":1,"short_signals":1,"mean_forward_return":0.01,"median_forward_return":0.01,"win_rate":0.5}], out)
    text = out.read_text(encoding="utf-8")
    assert "Horizon (bars)" in text
    assert "| 3 |" in text


def test_write_summary_report_empty_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        write_summary_report([], tmp_path / "fail.md")
