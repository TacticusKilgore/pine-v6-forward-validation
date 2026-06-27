from __future__ import annotations

from typing import Any
import pandas as pd

from src.pine_parity.rolling import rolling_highest, rolling_lowest


def iax(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    length = int(config.get("range_length", config.get("sweep_lookback", 20)))
    out = df.copy().reset_index(drop=True)
    out["range_high"] = rolling_highest(out["high"], length).shift(1)
    out["range_low"] = rolling_lowest(out["low"], length).shift(1)
    states: list[str | None] = []
    signals = [0] * len(out)
    scores: list[float] = []
    for i in range(len(out)):
        rh, rl = out.at[i, "range_high"], out.at[i, "range_low"]
        if pd.isna(rh) or pd.isna(rl):
            states.append(None)
            scores.append(0.0)
            continue
        if out.at[i, "high"] > rh and out.at[i, "close"] < rh:
            states.append("sweep_up")
            signals[i] = -1
            scores.append(float((out.at[i, "high"] - rh) / rh))
        elif out.at[i, "low"] < rl and out.at[i, "close"] > rl:
            states.append("sweep_down")
            signals[i] = 1
            scores.append(float((rl - out.at[i, "low"]) / rl))
        else:
            states.append("inside")
            scores.append(0.0)
    out["iax_state"] = states
    out["signal"] = signals
    out["score"] = scores
    out["long_signal"] = (out["signal"] == 1).astype(int)
    out["short_signal"] = (out["signal"] == -1).astype(int)
    return out
