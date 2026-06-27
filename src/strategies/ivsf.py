from __future__ import annotations

import numpy as np
import pandas as pd

from src.pine_parity.indicators import add_common_features


class IVSFStrategy:
    """Minimal Internal Value Shift Field mirror for validation plumbing."""

    name = "ivsf"

    @classmethod
    def from_config(cls, cfg: dict) -> "IVSFStrategy":
        return cls()

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_common_features(df)
        trend_up = (out["ema20"] > out["ema200"]) & (out["close"] > out["vwap_d"])
        trend_down = (out["ema20"] < out["ema200"]) & (out["close"] < out["vwap_d"])
        expansion = ((out["high"] - out["low"]) / out["atr"]) > 1.15
        out["EXP_score"] = np.where(trend_up | trend_down, 55, 25) + np.where(expansion, 25, 0)
        out["EXP_longSignal"] = trend_up & expansion & (out["EXP_score"] >= 75)
        out["EXP_shortSignal"] = trend_down & expansion & (out["EXP_score"] >= 75)
        out["EXP_state"] = np.select([out["EXP_longSignal"], out["EXP_shortSignal"]], ["Active Long", "Active Short"], default="Neutral")
        return out
