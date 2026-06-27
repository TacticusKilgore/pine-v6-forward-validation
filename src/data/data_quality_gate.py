from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import pandas as pd

from src.data.schema import normalize_ohlcv_frame, validate_ohlcv_frame


@dataclass(frozen=True)
class DataQualityGateReport:
    symbol: str
    timeframe: str
    rows: int
    start: str | None
    end: str | None
    missing_candles: int
    duplicate_timestamps: int
    non_positive_prices: int
    negative_volume: int
    inferred_timeframe: str | None
    passed: bool
    gaps: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def build_data_quality_report(df: pd.DataFrame, symbol: str, timeframe: str) -> DataQualityGateReport:
    duplicate_timestamps = _duplicate_count(df)
    normalized = normalize_ohlcv_frame(df)
    structural = validate_ohlcv_frame(normalized)
    delta = _delta(timeframe) or _delta(structural.inferred_timeframe or "")
    gaps = _gaps(normalized.index, delta)
    missing_candles = sum(int(g["missing_candles"]) for g in gaps)
    passed = structural.passed and duplicate_timestamps == 0 and missing_candles == 0
    return DataQualityGateReport(
        symbol=symbol,
        timeframe=timeframe,
        rows=structural.rows,
        start=structural.start.isoformat() if structural.start is not None else None,
        end=structural.end.isoformat() if structural.end is not None else None,
        missing_candles=int(missing_candles),
        duplicate_timestamps=duplicate_timestamps,
        non_positive_prices=structural.non_positive_prices,
        negative_volume=structural.negative_volume,
        inferred_timeframe=structural.inferred_timeframe,
        passed=bool(passed),
        gaps=gaps,
    )


def write_data_quality_report(report: DataQualityGateReport, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _duplicate_count(df: pd.DataFrame) -> int:
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        return int(ts.duplicated().sum())
    if isinstance(df.index, pd.DatetimeIndex):
        return int(pd.to_datetime(df.index, utc=True).duplicated().sum())
    return 0


def _delta(value: str) -> pd.Timedelta | None:
    raw = str(value).lower().strip()
    units = [("min", "minutes"), ("m", "minutes"), ("h", "hours"), ("d", "days"), ("s", "seconds")]
    for suffix, unit in units:
        if raw.endswith(suffix) and raw[: -len(suffix)].isdigit():
            return pd.Timedelta(**{unit: int(raw[: -len(suffix)])})
    return None


def _gaps(index: pd.DatetimeIndex, delta: pd.Timedelta | None) -> list[dict]:
    if delta is None or len(index) < 2:
        return []
    idx = pd.to_datetime(index, utc=True).sort_values()
    out: list[dict] = []
    for i in range(1, len(idx)):
        observed = idx[i] - idx[i - 1]
        missing = int(observed / delta) - 1 if observed > delta else 0
        if missing > 0:
            out.append({"start": idx[i - 1].isoformat(), "end": idx[i].isoformat(), "missing_candles": missing})
    return out
