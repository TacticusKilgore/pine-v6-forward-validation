from __future__ import annotations

import pandas as pd
from src.pine_parity.rolling import rolling_highest, rolling_lowest


def generate_signals(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    cfg = (config or {}).get("params", config or {})
    lookback = int(cfg.get("sweep_lookback", 36))
    out = df.copy()
    prev_high = rolling_highest(out["high"], lookback).shift(1)
    prev_low = rolling_lowest(out["low"], lookback).shift(1)
    out["score"] = 0.0
    out["signal"] = 0
    out.loc[(out["low"] < prev_low) & (out["close"] > prev_low), ["score", "signal"]] = [65.0, 1]
    out.loc[(out["high"] > prev_high) & (out["close"] < prev_high), ["score", "signal"]] = [65.0, -1]
    return out
