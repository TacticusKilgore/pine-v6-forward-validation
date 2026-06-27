from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json

import pandas as pd

from src.pine_parity.parity_checker import ParityConfig, check_parity

SIGNAL_COLUMNS = ("EXP_longSignal", "EXP_shortSignal")


@dataclass(frozen=True)
class ParityEvidenceReport:
    strategy: str
    symbol: str
    timeframe: str
    pine_export_path: str
    python_output_path: str
    passed: bool
    severity: str
    checked_rows: int
    common_columns: list[str]
    missing_columns: list[str]
    mismatch_count: int
    critical_mismatches: int
    signal_bar_match_rate: float | None
    direction_match_rate: float | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_parity_evidence_report(
    *,
    pine_export_path: str | Path,
    python_output_path: str | Path,
    strategy: str,
    symbol: str,
    timeframe: str,
    root: str | Path = ".",
    config: ParityConfig | None = None,
) -> ParityEvidenceReport:
    root_path = Path(root)
    pine_path = root_path / pine_export_path
    py_path = root_path / python_output_path

    if not pine_path.is_file():
        return _error_report(strategy, symbol, timeframe, str(pine_export_path), str(python_output_path), f"Pine export not found: {pine_export_path}")
    if not py_path.is_file():
        return _error_report(strategy, symbol, timeframe, str(pine_export_path), str(python_output_path), f"Python output not found: {python_output_path}")

    pine = pd.read_csv(pine_path)
    py = pd.read_csv(py_path)
    result = check_parity(pine, py, config or ParityConfig())
    signal_bar_rate = _signal_bar_match_rate(pine, py)
    direction_rate = _direction_match_rate(pine, py)
    mismatch_count = int(len(result.mismatches))
    critical = _critical_mismatch_count(result.mismatches, result.missing_columns)
    passed = bool(result.passed and critical == 0 and signal_bar_rate == 1.0 and direction_rate == 1.0)
    severity = "GO" if passed else "HOLD"
    message = "parity evidence passed" if passed else "parity evidence has mismatches or incomplete signal alignment"

    return ParityEvidenceReport(
        strategy=strategy,
        symbol=symbol,
        timeframe=timeframe,
        pine_export_path=str(pine_export_path),
        python_output_path=str(python_output_path),
        passed=passed,
        severity=severity,
        checked_rows=int(result.checked_rows),
        common_columns=list(result.common_columns),
        missing_columns=list(result.missing_columns),
        mismatch_count=mismatch_count,
        critical_mismatches=critical,
        signal_bar_match_rate=signal_bar_rate,
        direction_match_rate=direction_rate,
        message=message,
    )


def write_parity_evidence_json(report: ParityEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return out


def write_parity_evidence_markdown(report: ParityEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Real Parity Evidence Report",
        "",
        f"Strategy: `{report.strategy}`",
        f"Symbol: `{report.symbol}`",
        f"Timeframe: `{report.timeframe}`",
        f"Passed: `{report.passed}`",
        f"Severity: `{report.severity}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Checked rows | {report.checked_rows} |",
        f"| Mismatch count | {report.mismatch_count} |",
        f"| Critical mismatches | {report.critical_mismatches} |",
        f"| Signal-bar match rate | {_fmt_rate(report.signal_bar_match_rate)} |",
        f"| Direction match rate | {_fmt_rate(report.direction_match_rate)} |",
        "",
        "## Inputs",
        "",
        f"- Pine export: `{report.pine_export_path}`",
        f"- Python output: `{report.python_output_path}`",
        "",
        "## Message",
        "",
        report.message,
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _signal_bar_match_rate(pine: pd.DataFrame, py: pd.DataFrame) -> float | None:
    pine_n = _normalize_for_signal(pine)
    py_n = _normalize_for_signal(py)
    if not all(col in pine_n.columns and col in py_n.columns for col in SIGNAL_COLUMNS):
        return None
    common = pine_n.index.intersection(py_n.index)
    if len(common) == 0:
        return 0.0
    pine_signal = _signal_present(pine_n.loc[common])
    py_signal = _signal_present(py_n.loc[common])
    return float((pine_signal == py_signal).mean())


def _direction_match_rate(pine: pd.DataFrame, py: pd.DataFrame) -> float | None:
    pine_n = _normalize_for_signal(pine)
    py_n = _normalize_for_signal(py)
    if not all(col in pine_n.columns and col in py_n.columns for col in SIGNAL_COLUMNS):
        return None
    common = pine_n.index.intersection(py_n.index)
    if len(common) == 0:
        return 0.0
    pine_dir = _direction(pine_n.loc[common])
    py_dir = _direction(py_n.loc[common])
    signal_rows = (pine_dir != 0) | (py_dir != 0)
    if int(signal_rows.sum()) == 0:
        return 1.0
    return float((pine_dir[signal_rows] == py_dir[signal_rows]).mean())


def _normalize_for_signal(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
        out = out.set_index("timestamp")
    elif isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index, utc=True)
    else:
        raise ValueError("parity evidence inputs require timestamp column or DatetimeIndex")
    return out.sort_index()


def _signal_present(df: pd.DataFrame) -> pd.Series:
    return _as_bool(df["EXP_longSignal"]) | _as_bool(df["EXP_shortSignal"])


def _direction(df: pd.DataFrame) -> pd.Series:
    long_signal = _as_bool(df["EXP_longSignal"])
    short_signal = _as_bool(df["EXP_shortSignal"])
    out = pd.Series(0, index=df.index, dtype=int)
    out.loc[long_signal & ~short_signal] = 1
    out.loc[short_signal & ~long_signal] = -1
    return out


def _as_bool(series: pd.Series) -> pd.Series:
    return series.map(lambda value: str(value).strip().lower() in {"true", "1", "yes"}).astype(bool)


def _critical_mismatch_count(mismatches: pd.DataFrame, missing_columns: list[str]) -> int:
    if not missing_columns and mismatches.empty:
        return 0
    if mismatches.empty:
        return len(missing_columns)
    critical_cols = {"EXP_longSignal", "EXP_shortSignal", "EXP_state"}
    count = len(missing_columns)
    if "column" in mismatches.columns:
        count += int(mismatches["column"].isin(critical_cols).sum())
        count += int((mismatches["column"] == "<index>").sum())
    else:
        count += int(len(mismatches))
    return count


def _fmt_rate(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _error_report(strategy: str, symbol: str, timeframe: str, pine_path: str, py_path: str, message: str) -> ParityEvidenceReport:
    return ParityEvidenceReport(
        strategy=strategy,
        symbol=symbol,
        timeframe=timeframe,
        pine_export_path=pine_path,
        python_output_path=py_path,
        passed=False,
        severity="HOLD",
        checked_rows=0,
        common_columns=[],
        missing_columns=[],
        mismatch_count=0,
        critical_mismatches=1,
        signal_bar_match_rate=None,
        direction_match_rate=None,
        message=message,
    )
