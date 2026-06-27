from __future__ import annotations

import pandas as pd
from src.pine_parity.rolling import pine_ema


def generate_signals(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    out = df.copy()
    ema20 = pine_ema(out["close"], 20)
    out["score"] = 50.0
    out["signal"] = 0
    out.loc[(out["low"] <= ema20) & (out["close"] > ema20), "signal"] = 1
    out.loc[(out["high"] >= ema20) & (out["close"] < ema20), "signal"] = -1
    return out
