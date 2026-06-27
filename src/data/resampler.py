from __future__ import annotations

import pandas as pd
from src.data.csv_loader import normalize_ohlcv


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    freq = timeframe.replace("m", "min")
    src = normalize_ohlcv(df).set_index("timestamp")
    out = src.resample(freq, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return normalize_ohlcv(out.dropna().reset_index())
