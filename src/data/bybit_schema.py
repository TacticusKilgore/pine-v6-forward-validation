from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

REQUIRED_BYBIT_OHLCV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class BybitSchemaReport:
    passed: bool
    rows: int
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_bybit_ohlcv_schema(df: pd.DataFrame) -> BybitSchemaReport:
    errors: list[str] = []
    warnings: list[str] = []

    missing = [column for column in REQUIRED_BYBIT_OHLCV_COLUMNS if column not in df.columns]
    if missing:
        errors.append(f"missing required columns: {missing}")
        return BybitSchemaReport(False, int(len(df)), errors, warnings)

    try:
        timestamps = pd.to_datetime(df["timestamp"], utc=True)
    except Exception as exc:
        errors.append(f"timestamp parse failed: {exc}")
        return BybitSchemaReport(False, int(len(df)), errors, warnings)

    if timestamps.isna().any():
        errors.append("timestamp contains null or unparseable values")
    if timestamps.duplicated().any():
        errors.append("timestamp contains duplicates")
    if not timestamps.is_monotonic_increasing:
        errors.append("timestamp must be sorted ascending")

    numeric_columns = ["open", "high", "low", "close", "volume"]
    numeric = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    for column in numeric_columns:
        if numeric[column].isna().any():
            errors.append(f"{column} contains non-numeric values")

    if not errors:
        price_columns = ["open", "high", "low", "close"]
        for column in price_columns:
            if (numeric[column] <= 0).any():
                errors.append(f"{column} must be positive")
        if (numeric["volume"] < 0).any():
            errors.append("volume must be non-negative")
        if (numeric["high"] < numeric[["open", "close", "low"]].max(axis=1)).any():
            errors.append("high must be greater than or equal to open, close and low")
        if (numeric["low"] > numeric[["open", "close", "high"]].min(axis=1)).any():
            errors.append("low must be less than or equal to open, close and high")

    if len(df) == 0:
        warnings.append("dataset is empty")

    return BybitSchemaReport(not errors, int(len(df)), errors, warnings)


def validate_bybit_ohlcv(df: pd.DataFrame) -> None:
    report = inspect_bybit_ohlcv_schema(df)
    if not report.passed:
        raise ValueError("Bybit OHLCV schema validation failed: " + "; ".join(report.errors))
