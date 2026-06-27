from __future__ import annotations

import pandas as pd
from src.pine_parity.indicators import atr, hlc3
from src.pine_parity.rolling import pine_sma


def generate_signals(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    cfg = (config or {}).get("params", config or {})
    out = df.copy()
    out["atr"] = atr(out, int(cfg.get("atr_len", 14)))
    mid = pine_sma(hlc3(out), int(cfg.get("value_lookback", 48)))
    width = out["atr"] * float(cfg.get("value_width_atr", 0.75))
    out["score"] = 0.0
    out["signal"] = 0
    out.loc[(out["close"] > mid - width) & (out["close"] < mid), ["score", "signal"]] = [60.0, 1]
    out.loc[(out["close"] < mid + width) & (out["close"] > mid), ["score", "signal"]] = [60.0, -1]
    return out
