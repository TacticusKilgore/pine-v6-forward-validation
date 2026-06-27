from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import pandas as pd


@dataclass(frozen=True)
class ReconciliationReport:
    rows: int
    matched_rows: int
    signal_mismatches: int
    direction_match_rate: float
    passed: bool
    mismatches: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def reconcile_signal_frames(pine_export: pd.DataFrame, shadow_output: pd.DataFrame) -> ReconciliationReport:
    pine = _normalize(pine_export, "pine")
    shadow = _normalize(shadow_output, "shadow")
    merged = pine.merge(shadow, on="timestamp", how="outer", indicator=True).sort_values("timestamp")
    mismatches: list[dict] = []
    matched = 0
    for _, row in merged.iterrows():
        ts = str(row["timestamp"])
        if row["_merge"] != "both":
            mismatches.append({"timestamp": ts, "reason": str(row["_merge"])})
            continue
        matched += 1
        pine_dir = row["pine_direction"]
        shadow_dir = row["shadow_direction"]
        if pine_dir != shadow_dir:
            mismatches.append({"timestamp": ts, "pine": pine_dir, "shadow": shadow_dir})
    rows = int(len(merged))
    signal_mismatches = int(len(mismatches))
    direction_match_rate = 1.0 if matched == 0 else float((matched - signal_mismatches) / matched)
    passed = signal_mismatches == 0 and rows > 0
    return ReconciliationReport(
        rows=rows,
        matched_rows=matched,
        signal_mismatches=signal_mismatches,
        direction_match_rate=direction_match_rate,
        passed=passed,
        mismatches=mismatches[:100],
    )


def write_reconciliation_report(report: ReconciliationReport, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _normalize(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = df.copy()
    if "timestamp" not in out.columns:
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index().rename(columns={out.index.name or "index": "timestamp"})
        else:
            raise ValueError("reconciliation input requires timestamp")
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    long_col = "EXP_longSignal"
    short_col = "EXP_shortSignal"
    if long_col not in out.columns:
        out[long_col] = False
    if short_col not in out.columns:
        out[short_col] = False
    out[f"{prefix}_direction"] = [
        _direction(long_value, short_value) for long_value, short_value in zip(out[long_col], out[short_col])
    ]
    return out[["timestamp", f"{prefix}_direction"]]


def _direction(long_value, short_value) -> str:
    long_signal = _to_bool(long_value)
    short_signal = _to_bool(short_value)
    if long_signal and not short_signal:
        return "long"
    if short_signal and not long_signal:
        return "short"
    if long_signal and short_signal:
        return "conflict"
    return "flat"


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}
