from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import pandas as pd

REQUIRED_EXPORT_COLUMNS = (
    "timestamp",
    "symbol",
    "timeframe",
    "EXP_state",
    "EXP_regime",
    "EXP_bias",
    "EXP_score",
    "EXP_longSignal",
    "EXP_shortSignal",
    "EXP_longBlocker",
    "EXP_shortBlocker",
    "EXP_entryPrice",
    "EXP_stopPrice",
    "EXP_tp1",
    "EXP_tp2",
    "EXP_tp3",
    "EXP_cooldown",
    "EXP_invalidReason",
)

BOOL_COLUMNS = ("EXP_longSignal", "EXP_shortSignal")


@dataclass(frozen=True)
class ExportContractReport:
    rows: int
    passed: bool
    missing_required_columns: list[str]
    extra_columns: list[str]
    duplicate_timestamps: int
    invalid_timestamps: int
    start: str | None
    end: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_export_frame(df: pd.DataFrame, fill_missing: bool = True) -> pd.DataFrame:
    out = df.copy()
    if "timestamp" not in out.columns:
        raise ValueError("Pine export must contain a timestamp column")
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    for col in REQUIRED_EXPORT_COLUMNS:
        if col not in out.columns and fill_missing:
            out[col] = "not_available"
    for col in BOOL_COLUMNS:
        if col in out.columns:
            out[col] = out[col].map(parse_pine_bool)
    return out.sort_values("timestamp")


def validate_export_contract(df: pd.DataFrame) -> ExportContractReport:
    missing = [c for c in REQUIRED_EXPORT_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in REQUIRED_EXPORT_COLUMNS]
    ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce") if "timestamp" in df.columns else pd.Series(dtype="datetime64[ns, UTC]")
    invalid = int(ts.isna().sum()) if len(ts) else 1
    dupes = int(ts.duplicated().sum()) if len(ts) else 0
    normalized = normalize_export_frame(df, fill_missing=True) if "timestamp" in df.columns else pd.DataFrame()
    start = normalized["timestamp"].min().isoformat() if not normalized.empty and normalized["timestamp"].notna().any() else None
    end = normalized["timestamp"].max().isoformat() if not normalized.empty and normalized["timestamp"].notna().any() else None
    passed = len(missing) == 0 and invalid == 0 and dupes == 0 and len(df) > 0
    return ExportContractReport(
        rows=int(len(df)),
        passed=bool(passed),
        missing_required_columns=missing,
        extra_columns=extra,
        duplicate_timestamps=dupes,
        invalid_timestamps=invalid,
        start=start,
        end=end,
    )


def write_export_contract_report(report: ExportContractReport, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def parse_pine_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", "", "nan", "none", "not_available"}:
        return False
    return bool(value)
