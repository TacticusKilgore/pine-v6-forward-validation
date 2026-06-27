from __future__ import annotations

import pandas as pd
from src.pine_parity.rolling import pine_ema


def generate_signals(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    out = df.copy()
    ema = pine_ema(out["close"], int((config or {}).get("ema_len", 20)))
    out["score"] = 50.0
    out["signal"] = 0
    out.loc[out["close"] > ema, "signal"] = 1
    out.loc[out["close"] < ema, "signal"] = -1
    return out
