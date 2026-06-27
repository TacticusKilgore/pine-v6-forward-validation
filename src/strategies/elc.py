from __future__ import annotations

import numpy as np
import pandas as pd

from src.pine_parity.indicators import add_common_features


class ELCStrategy:
    """EMA20 Ladder Continuation mirror for validation plumbing."""

    name = "elc"

    @classmethod
    def from_config(cls, cfg: dict) -> "ELCStrategy":
        return cls()

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_common_features(df)
        atr = out["atr"]
        touch_ema20 = (out["low"] <= out["ema20"] + atr * 0.18) & (out["high"] >= out["ema20"] - atr * 0.18)
        ladder_up = (out["ema20"] > out["ema20"].shift(1)) & (out["close"] > out["ema20"]) & (out["ema20"] > out["ema200"])
        ladder_down = (out["ema20"] < out["ema20"].shift(1)) & (out["close"] < out["ema20"]) & (out["ema20"] < out["ema200"])
        momentum = out["body_eff"] > 0.45
        out["EXP_score"] = np.where((ladder_up | ladder_down), 55, 0) + np.where(touch_ema20, 20, 0) + np.where(momentum, 25, 0)
        out["EXP_longSignal"] = ladder_up & touch_ema20 & momentum & (out["EXP_score"] >= 75)
        out["EXP_shortSignal"] = ladder_down & touch_ema20 & momentum & (out["EXP_score"] >= 75)
        out["EXP_state"] = np.select([out["EXP_longSignal"], out["EXP_shortSignal"]], ["Active Long", "Active Short"], default="Neutral")
        return out
