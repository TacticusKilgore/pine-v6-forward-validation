"""
Bybit OHLCV loader.

This module provides helper functions to load OHLCV data for Bybit perpetual
contracts. It supports both local CSV loading (the default) and fetching
live data via the `ccxt` library if available. Live loading requires the
optional dependency ``ccxt`` to be installed and may require rate limiting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

import pandas as pd

from .csv_loader import load_csv


def load_bybit_ohlcv(
    symbol: str,
    timeframe: str,
    *,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    live: bool = False,
    data_dir: str | Path = "data/raw",
) -> pd.DataFrame:
    """Load Bybit perpetual OHLCV data.

    By default this function loads pre‑downloaded CSV files from ``data_dir`` with
    file names in the format ``{symbol}_{timeframe}.csv``. If ``live=True`` is
    passed, the function attempts to fetch data via the `ccxt` library. Live
    fetching requires the optional ``ccxt`` dependency and will raise an error if
    it is not installed.

    Args:
        symbol: The trading pair symbol (e.g. ``BTCUSDT``).
        timeframe: The timeframe string (e.g. ``5m``, ``1h``). When loading
            pre‑saved CSVs, dots or slashes in the timeframe should be avoided.
        limit: The maximum number of bars to fetch when live loading. If None,
            the API default is used.
        start: ISO datetime string for the start time when live loading.
        end: ISO datetime string for the end time when live loading.
        live: If True, attempt to fetch data live via ``ccxt``. Otherwise read
            from CSV.
        data_dir: Directory where local CSVs are stored.

    Returns:
        A DataFrame containing OHLCV data with columns ``timestamp``, ``open``,
        ``high``, ``low``, ``close``, ``volume``.

    Raises:
        ImportError: If ``live=True`` and the optional dependency is not installed.
        FileNotFoundError: If the expected CSV file does not exist when
            ``live=False``.
    """
    if live:
        try:
            import ccxt  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "Live loading requires the optional 'ccxt' package. Install via 'pip install ccxt'."
            ) from exc

        # Create exchange instance
        exchange = ccxt.bybit({"enableRateLimit": True})
        if not hasattr(exchange, "fetch_ohlcv"):
            raise RuntimeError("The ccxt Bybit exchange does not implement fetch_ohlcv")
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if start is not None:
            kwargs["since"] = int(pd.to_datetime(start, utc=True).timestamp() * 1000)
        if end is not None:
            kwargs["end_time"] = int(pd.to_datetime(end, utc=True).timestamp() * 1000)
        # Fetch data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, **kwargs)
        columns = ["timestamp", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(ohlcv, columns=columns)
        # Convert timestamp from milliseconds to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df
    else:
        file_name = f"{symbol}_{timeframe}.csv"
        file_path = Path(data_dir) / file_name
        return load_csv(file_path, validate=True)
