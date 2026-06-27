"""
CSV loader and validator for OHLCV data.

This module defines helper functions to load CSV files containing OHLCV data and
to validate that the data conforms to expected requirements. Validating data
early helps catch errors such as missing columns, unsorted indices or invalid
price/volume values before they propagate into strategy evaluations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def load_csv(path: str | Path, *, validate: bool = True) -> pd.DataFrame:
    """Load an OHLCV CSV file into a DataFrame and optionally validate it.

    Args:
        path: Path to the CSV file.
        validate: Whether to validate the loaded DataFrame using ``validate_ohlcv``.

    Returns:
        A pandas DataFrame with the loaded data.

    Raises:
        ValueError: If validation fails.
    """
    file_path = Path(path)
    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise ValueError(f"Could not load CSV {file_path}: {exc}") from exc

    if validate:
        validate_ohlcv(df)
    return df


def validate_ohlcv(df: pd.DataFrame) -> None:
    """Validate an OHLCV DataFrame for required columns and integrity.

    The function performs several checks:

    * All required columns are present.
    * ``timestamp`` is monotonically increasing and unique.
    * Price columns are non‑negative and respect ``high >= open/close/low`` and
      ``low <= open/close/high``.
    * Volume is non‑negative.
    * The index order matches the chronological order of ``timestamp``.

    Args:
        df: DataFrame to validate.

    Raises:
        ValueError: If any of the validation checks fail.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Convert timestamp to datetime for validation, do not modify original column
    try:
        ts = pd.to_datetime(df["timestamp"], utc=True)
    except Exception as exc:
        raise ValueError(f"Column 'timestamp' could not be parsed as datetime: {exc}") from exc

    # Check monotonic increasing order
    if not ts.is_monotonic_increasing:
        raise ValueError("Timestamps must be monotonic increasing")
    # Check duplicates
    if ts.duplicated().any():
        dupes = ts[ts.duplicated()].unique()
        raise ValueError(f"Duplicate timestamps found: {dupes}")

    # Check price and volume columns
    for col in ["open", "high", "low", "close", "volume"]:
        if (df[col] < 0).any():
            raise ValueError(f"Column '{col}' contains negative values")
    # High/Low consistency checks
    if ((df["high"] < df[["open", "close", "low"]].max(axis=1))).any():
        raise ValueError("High price must be >= open, close and low on each row")
    if ((df["low"] > df[["open", "close", "high"]].min(axis=1))).any():
        raise ValueError("Low price must be <= open, close and high on each row")

    # Ensure DataFrame order matches timestamp order
    if not df.index.is_monotonic_increasing:
        # Sort by timestamp if index is not monotonic; require that index is simple range
        if not isinstance(df.index, pd.RangeIndex):
            raise ValueError("DataFrame index must be monotonic increasing or a simple range index")
        # Sorting is not allowed: we require input to already be sorted for reproducibility
        # If index does not reflect the order of the timestamps, raise error
        if not (df["timestamp"].astype(str) == df["timestamp"].astype(str).sort_values()).all():
            raise ValueError("DataFrame rows are not in ascending timestamp order")
