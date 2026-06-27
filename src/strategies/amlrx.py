from __future__ import annotations

from typing import Any
import pandas as pd

from src.pine_parity.indicators import atr, hlc3
from src.pine_parity.rolling import pine_sma


def amlrx(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    atr_len = int(config.get("atr_length", config.get("atr_len", 14)))
    mid_len = int(config.get("value_mid_length", config.get("value_lookback", 20)))
    width_mult = float(config.get("width_mult", config.get("value_width_atr", 1.0)))
    out = df.copy().reset_index(drop=True)
    out["atr"] = atr(out["high"], out["low"], out["close"], atr_len)
    out["value_mid"] = pine_sma(hlc3(out["high"], out["low"], out["close"]), mid_len)
    out["value_upper"] = out["value_mid"] + out["atr"] * width_mult
    out["value_lower"] = out["value_mid"] - out["atr"] * width_mult
    states: list[str | None] = []
    signals = [0] * len(out)
    for i in range(len(out)):
        if pd.isna(out.at[i, "value_mid"]) or pd.isna(out.at[i, "atr"]):
            states.append(None)
            continue
        close = out.at[i, "close"]
        upper = out.at[i, "value_upper"]
        lower = out.at[i, "value_lower"]
        state = "above" if close > upper else "below" if close < lower else "inside"
        states.append(state)
        if i > 0 and states[i - 1] == "below" and state == "inside":
            signals[i] = 1
        elif i > 0 and states[i - 1] == "above" and state == "inside":
            signals[i] = -1
    out["amlrx_state"] = states
    out["signal"] = signals
    out["score"] = ((out["close"] - out["value_mid"]) / out["atr"]).fillna(0.0)
    out["long_signal"] = (out["signal"] == 1).astype(int)
    out["short_signal"] = (out["signal"] == -1).astype(int)
    return out
