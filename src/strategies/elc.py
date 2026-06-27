from __future__ import annotations

from typing import Any
import pandas as pd


def elc(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    threshold = float(config.get("threshold", 0.005))
    out = df.copy().reset_index(drop=True)
    prev_close = out["close"].shift(1)
    states: list[str | None] = []
    signals = [0] * len(out)
    scores: list[float] = []
    for i in range(len(out)):
        if i == 0 or pd.isna(prev_close.iat[i]) or prev_close.iat[i] <= 0:
            states.append(None)
            scores.append(0.0)
            continue
        pc = float(prev_close.iat[i])
        long_move = (float(out.at[i, "high"]) - pc) / pc
        short_move = (pc - float(out.at[i, "low"])) / pc
        if long_move > threshold:
            states.append("breakout_long")
            signals[i] = 1
            scores.append(long_move)
        elif short_move > threshold:
            states.append("breakout_short")
            signals[i] = -1
            scores.append(short_move)
        else:
            states.append("inside")
            scores.append(0.0)
    out["elc_state"] = states
    out["signal"] = signals
    out["score"] = scores
    out["long_signal"] = (out["signal"] == 1).astype(int)
    out["short_signal"] = (out["signal"] == -1).astype(int)
    return out
