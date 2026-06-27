from __future__ import annotations

import pandas as pd
import pytest

from src.data.bybit_schema import inspect_bybit_ohlcv_schema, validate_bybit_ohlcv


def valid_bybit_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z", "2026-01-01T00:05:00Z", "2026-01-01T00:10:00Z"],
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [10.0, 11.0, 12.0],
        }
    )


def test_validate_bybit_ohlcv_accepts_valid_frame() -> None:
    validate_bybit_ohlcv(valid_bybit_df())
    report = inspect_bybit_ohlcv_schema(valid_bybit_df())
    assert report.passed
    assert report.rows == 3


def test_validate_bybit_ohlcv_rejects_missing_column() -> None:
    df = valid_bybit_df().drop(columns=["close"])
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)


def test_validate_bybit_ohlcv_rejects_duplicate_timestamps() -> None:
    df = valid_bybit_df()
    df.loc[2, "timestamp"] = df.loc[1, "timestamp"]
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)


def test_validate_bybit_ohlcv_rejects_unsorted_timestamps() -> None:
    df = valid_bybit_df()
    df.loc[2, "timestamp"] = "2025-12-31T23:55:00Z"
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)


def test_validate_bybit_ohlcv_rejects_invalid_high_low_relation() -> None:
    df = valid_bybit_df()
    df.loc[1, "high"] = 99.5
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)


def test_validate_bybit_ohlcv_rejects_non_positive_price() -> None:
    df = valid_bybit_df()
    df.loc[1, "open"] = 0.0
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)


def test_validate_bybit_ohlcv_rejects_negative_volume() -> None:
    df = valid_bybit_df()
    df.loc[1, "volume"] = -1.0
    with pytest.raises(ValueError):
        validate_bybit_ohlcv(df)
