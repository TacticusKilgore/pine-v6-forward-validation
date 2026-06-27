"""
OHLCV resampling utilities.

This module defines functions to resample OHLCV data between different timeframes.
It relies on pandas resampling and ensures that the output respects the
traditional OHLC aggregation semantics: open = first, high = max, low = min,
close = last, volume = sum.
"""

from __future__ import annotations

from typing import Union

import pandas as pd

from .csv_loader import REQUIRED_COLUMNS


def resample_ohlcv(
    df: pd.DataFrame,
    rule: str,
    *,
    label: str = "right",
    closed: str = "right",
    ts_col: str = "timestamp",
) -> pd.DataFrame:
    """Resample an OHLCV DataFrame to a different timeframe.

    Args:
        df: Input DataFrame with columns defined in ``REQUIRED_COLUMNS``.
        rule: Resample rule string compatible with pandas (e.g. '5T' for 5 minutes,
            '1H' for hourly, etc.).
        label: Whether to label the resampled bins as their left or right edge.
        closed: Whether intervals include the left or right bin edge.
        ts_col: Name of the timestamp column.

    Returns:
        A new DataFrame resampled to the specified rule. The timestamp column is
        preserved and converted to datetime in UTC.

    Raises:
        ValueError: If required columns are missing.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for resampling: {', '.join(missing)}")

    result = df.copy()
    # Convert timestamp to datetime index with UTC
    dt_index = pd.to_datetime(result[ts_col], utc=True)
    result.set_index(dt_index, inplace=True)

    ohlc = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    resampled = result.resample(rule, label=label, closed=closed).agg(ohlc)
    # Drop rows with missing values (e.g. due to incomplete aggregations)
    resampled = resampled.dropna()
    resampled = resampled.reset_index().rename(columns={"index": ts_col})
    # Ensure timestamp column remains in UTC and not timezone aware for downstream processing
    resampled[ts_col] = pd.to_datetime(resampled[ts_col], utc=True)
    return resampled
