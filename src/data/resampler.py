from __future__ import annotations

import pandas as pd


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample lower-timeframe OHLCV to a higher timeframe.

    Uses right-labeled, right-closed bars to mirror confirmed higher-timeframe bars.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must be indexed by timestamp")

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    out = df.resample(timeframe, label="right", closed="right").agg(agg)
    return out.dropna(subset=["open", "high", "low", "close"])
