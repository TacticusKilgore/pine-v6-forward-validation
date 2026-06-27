from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json

import pandas as pd

SIGNAL_LONG = "EXP_longSignal"
SIGNAL_SHORT = "EXP_shortSignal"
DEFAULT_HORIZONS = (3, 5, 10)


@dataclass(frozen=True)
class ForwardSignalEvidence:
    timestamp: str
    side: str
    entry_reference: float
    score: float | None
    signal_state: str | None
    risk_state: str | None
    regime: str | None
    results: dict[str, float | None]
    status: dict[str, str]
    failure_modes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForwardValidationEvidenceReport:
    strategy: str
    symbol: str
    timeframe: str
    passed: bool
    checked_rows: int
    signal_count: int
    horizons: list[int]
    side_summary: dict[str, dict[str, Any]]
    regime_summary: dict[str, dict[str, Any]]
    signals: list[ForwardSignalEvidence]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "passed": self.passed,
            "checked_rows": self.checked_rows,
            "signal_count": self.signal_count,
            "horizons": self.horizons,
            "side_summary": self.side_summary,
            "regime_summary": self.regime_summary,
            "signals": [row.to_dict() for row in self.signals],
            "message": self.message,
        }


def load_forward_input(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return normalize_forward_frame(df)


def normalize_forward_frame(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close", SIGNAL_LONG, SIGNAL_SHORT}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"forward input missing required columns: {missing}")
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    if out["timestamp"].duplicated().any():
        raise ValueError("forward input contains duplicate timestamps")
    if not out["timestamp"].is_monotonic_increasing:
        raise ValueError("forward input timestamps must be sorted ascending")
    return out.reset_index(drop=True)


def build_forward_validation_evidence_report(
    df: pd.DataFrame,
    *,
    strategy: str,
    symbol: str,
    timeframe: str,
    horizons: list[int] | tuple[int, ...] = DEFAULT_HORIZONS,
) -> ForwardValidationEvidenceReport:
    data = normalize_forward_frame(df)
    horizon_values = [int(h) for h in horizons]
    if not horizon_values or any(h <= 0 for h in horizon_values):
        raise ValueError("horizons must contain positive integers")

    signal_rows: list[ForwardSignalEvidence] = []
    for index, row in data.iterrows():
        side = _side(row)
        if side == "none":
            continue
        entry_reference = float(row["close"])
        results: dict[str, float | None] = {}
        status: dict[str, str] = {}
        failure_modes: dict[str, str] = {}
        for horizon in horizon_values:
            key = str(horizon)
            exit_index = index + horizon
            if exit_index >= len(data):
                results[key] = None
                status[key] = "open"
                failure_modes[key] = "insufficient_future_bars"
                continue
            exit_close = float(data.at[exit_index, "close"])
            result = (exit_close - entry_reference) / entry_reference if side == "long" else (entry_reference - exit_close) / entry_reference
            results[key] = float(result)
            status[key] = "closed"
            failure_modes[key] = _failure_mode(result)
        signal_rows.append(
            ForwardSignalEvidence(
                timestamp=str(row["timestamp"]),
                side=side,
                entry_reference=entry_reference,
                score=_optional_float(row, "EXP_score"),
                signal_state=_optional_str(row, "signal_state", "EXP_state"),
                risk_state=_optional_str(row, "risk_state", "EXP_riskState"),
                regime=_optional_str(row, "regime", "EXP_regime"),
                results=results,
                status=status,
                failure_modes=failure_modes,
            )
        )

    side_summary = _summarize_by(signal_rows, horizon_values, key_fn=lambda item: item.side)
    regime_summary = _summarize_by(signal_rows, horizon_values, key_fn=lambda item: item.regime or "unclassified")
    closed_any = any(any(status == "closed" for status in item.status.values()) for item in signal_rows)
    passed = len(signal_rows) > 0 and closed_any
    message = "forward evidence generated" if passed else "no closed forward signal evidence available"
    return ForwardValidationEvidenceReport(
        strategy=strategy,
        symbol=symbol,
        timeframe=timeframe,
        passed=passed,
        checked_rows=int(len(data)),
        signal_count=int(len(signal_rows)),
        horizons=horizon_values,
        side_summary=side_summary,
        regime_summary=regime_summary,
        signals=signal_rows,
        message=message,
    )


def write_forward_validation_evidence_json(report: ForwardValidationEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return out


def write_forward_validation_evidence_markdown(report: ForwardValidationEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Forward Validation Evidence Report",
        "",
        f"Strategy: `{report.strategy}`",
        f"Symbol: `{report.symbol}`",
        f"Timeframe: `{report.timeframe}`",
        f"Passed: `{report.passed}`",
        f"Checked rows: `{report.checked_rows}`",
        f"Signal count: `{report.signal_count}`",
        "",
        "## Side Summary",
        "",
        "| Side | Horizon | Closed | Open | Mean follow-through | Win rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for side, horizon_map in report.side_summary.items():
        for horizon, metrics in horizon_map.items():
            lines.append(
                f"| {side} | {horizon} | {metrics['closed']} | {metrics['open']} | {_fmt(metrics['mean_return'])} | {_fmt(metrics['win_rate'])} |"
            )
    lines.extend(["", "## Message", "", report.message])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _side(row: pd.Series) -> str:
    long_signal = _to_bool(row.get(SIGNAL_LONG, False))
    short_signal = _to_bool(row.get(SIGNAL_SHORT, False))
    if long_signal and not short_signal:
        return "long"
    if short_signal and not long_signal:
        return "short"
    if long_signal and short_signal:
        return "conflict"
    return "none"


def _to_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _optional_float(row: pd.Series, column: str) -> float | None:
    if column not in row or pd.isna(row[column]):
        return None
    return float(row[column])


def _optional_str(row: pd.Series, *columns: str) -> str | None:
    for column in columns:
        if column in row and not pd.isna(row[column]):
            return str(row[column])
    return None


def _failure_mode(result: float) -> str:
    if result > 0:
        return "follow_through_positive"
    if result < 0:
        return "follow_through_negative"
    return "flat"


def _summarize_by(
    signals: list[ForwardSignalEvidence],
    horizons: list[int],
    *,
    key_fn,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[ForwardSignalEvidence]] = {}
    for item in signals:
        groups.setdefault(str(key_fn(item)), []).append(item)
    summary: dict[str, dict[str, Any]] = {}
    for group, rows in groups.items():
        summary[group] = {}
        for horizon in horizons:
            key = str(horizon)
            values = [item.results[key] for item in rows if item.results.get(key) is not None]
            open_count = sum(1 for item in rows if item.status.get(key) == "open")
            closed_count = len(values)
            mean_return = None if not values else float(pd.Series(values, dtype="float64").mean())
            win_rate = None if not values else float((pd.Series(values, dtype="float64") > 0).mean())
            summary[group][key] = {
                "signals": len(rows),
                "closed": closed_count,
                "open": open_count,
                "mean_return": mean_return,
                "win_rate": win_rate,
            }
    return summary


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"
