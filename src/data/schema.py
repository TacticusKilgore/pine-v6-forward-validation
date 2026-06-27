from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pandas as pd

REQUIRED_OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
TIMESTAMP_COLUMN = "timestamp"


@dataclass(frozen=True)
class DataQualityReport:
    rows: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    duplicated_timestamps: int
    missing_values: dict[str, int]
    non_positive_prices: int
    negative_volume: int
    inferred_timeframe: str | None

    @property
    def passed(self) -> bool:
        return (
            self.rows > 0
            and self.duplicated_timestamps == 0
            and self.non_positive_prices == 0
            and self.negative_volume == 0
            and all(v == 0 for v in self.missing_values.values())
        )


def normalize_ohlcv_frame(df: pd.DataFrame, *, timestamp_column: str = TIMESTAMP_COLUMN) -> pd.DataFrame:
    """Return a UTC-indexed, sorted OHLCV frame with numeric columns.

    Accepted input forms:
    - a DataFrame with a `timestamp` column
    - a DataFrame already indexed by `DatetimeIndex`

    The function is deliberately strict for price columns and tolerant for volume NaN
    values, which are converted to 0.0 because some exchange exports omit empty volume.
    """
    out = df.copy()
    if timestamp_column in out.columns:
        out[timestamp_column] = pd.to_datetime(out[timestamp_column], utc=True)
        out = out.sort_values(timestamp_column).drop_duplicates(timestamp_column, keep="last")
        out = out.set_index(timestamp_column)
    elif isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index, utc=True)
        out = out.sort_index()
        out = out[~out.index.duplicated(keep="last")]
    else:
        raise ValueError("OHLCV data must contain a timestamp column or use a DatetimeIndex")

    missing = [c for c in REQUIRED_OHLCV_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    for col in REQUIRED_OHLCV_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["volume"] = out["volume"].fillna(0.0)
    return out


def infer_timeframe(index: pd.DatetimeIndex) -> str | None:
    """Infer the modal spacing of a timestamp index as a pandas frequency string."""
    if len(index) < 3:
        return None
    diffs = index.to_series().diff().dropna()
    if diffs.empty:
        return None
    mode = diffs.mode()
    if mode.empty:
        return None
    seconds = int(mode.iloc[0].total_seconds())
    if seconds <= 0:
        return None
    if seconds % 86_400 == 0:
        return f"{seconds // 86_400}D"
    if seconds % 3_600 == 0:
        return f"{seconds // 3_600}h"
    if seconds % 60 == 0:
        return f"{seconds // 60}min"
    return f"{seconds}s"


def validate_ohlcv_frame(df: pd.DataFrame, *, required_columns: Iterable[str] = REQUIRED_OHLCV_COLUMNS) -> DataQualityReport:
    """Validate structural OHLCV quality without mutating the input frame."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("OHLCV frame must use a DatetimeIndex before validation")
    required = list(required_columns)
    missing_columns = [c for c in required if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required OHLCV columns: {missing_columns}")

    missing_values = {c: int(df[c].isna().sum()) for c in required}
    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    non_positive_prices = int((df[price_cols] <= 0).any(axis=1).sum()) if price_cols else 0
    negative_volume = int((df["volume"] < 0).sum()) if "volume" in df.columns else 0
    return DataQualityReport(
        rows=int(len(df)),
        start=df.index.min() if len(df) else None,
        end=df.index.max() if len(df) else None,
        duplicated_timestamps=int(df.index.duplicated().sum()),
        missing_values=missing_values,
        non_positive_prices=non_positive_prices,
        negative_volume=negative_volume,
        inferred_timeframe=infer_timeframe(df.index),
    )


def require_valid_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    report = validate_ohlcv_frame(df)
    if not report.passed:
        raise ValueError(f"OHLCV quality gate failed: {report}")
    return df
