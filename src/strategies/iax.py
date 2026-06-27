from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.pine_parity.indicators import add_common_features


@dataclass(frozen=True)
class IAXParams:
    atr_len: int = 14
    range_len: int = 36
    volume_len: int = 20
    vol_effort_min: float = 1.22
    wick_min: float = 0.36
    close_location_min: float = 0.48
    max_penetration_atr: float = 1.15
    max_close_distance_atr: float = 0.42
    min_setup_score: float = 57.0
    min_entry_score: float = 65.0
    cooldown_bars: int = 8


class IAXStrategy:
    name = "iax"

    def __init__(self, params: IAXParams | None = None) -> None:
        self.params = params or IAXParams()

    @classmethod
    def from_config(cls, cfg: dict) -> "IAXStrategy":
        return cls(IAXParams(**cfg.get("params", {})))

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = add_common_features(df, atr_len=p.atr_len, volume_len=p.volume_len)
        prior_high = out["high"].shift(1).rolling(p.range_len, min_periods=p.range_len).max()
        prior_low = out["low"].shift(1).rolling(p.range_len, min_periods=p.range_len).min()

        sweep_high = out["high"] > prior_high
        sweep_low = out["low"] < prior_low
        reclaim_short = sweep_high & (out["close"] < prior_high)
        reclaim_long = sweep_low & (out["close"] > prior_low)

        pen_up_atr = (out["high"] - prior_high) / out["atr"]
        pen_down_atr = (prior_low - out["low"]) / out["atr"]
        vol_score = (out["vol_ratio"].fillna(0) / p.vol_effort_min).clip(0, 1) * 25
        wick_short_score = (out["upper_wick"].fillna(0) / p.wick_min).clip(0, 1) * 25
        wick_long_score = (out["lower_wick"].fillna(0) / p.wick_min).clip(0, 1) * 25
        close_short_score = ((1 - out["close_loc"].fillna(0)) / p.close_location_min).clip(0, 1) * 25
        close_long_score = (out["close_loc"].fillna(0) / p.close_location_min).clip(0, 1) * 25
        pen_short_score = (1 - (pen_up_atr / p.max_penetration_atr)).clip(0, 1) * 25
        pen_long_score = (1 - (pen_down_atr / p.max_penetration_atr)).clip(0, 1) * 25

        short_score = vol_score + wick_short_score + close_short_score + pen_short_score
        long_score = vol_score + wick_long_score + close_long_score + pen_long_score

        out["EXP_score"] = np.where(reclaim_long, long_score, np.where(reclaim_short, short_score, 0.0))
        out["EXP_longSignal"] = reclaim_long & (long_score >= p.min_entry_score)
        out["EXP_shortSignal"] = reclaim_short & (short_score >= p.min_entry_score)
        out["EXP_state"] = np.select(
            [out["EXP_longSignal"], out["EXP_shortSignal"], sweep_low, sweep_high],
            ["Active Long", "Active Short", "Armed Long", "Armed Short"],
            default="Neutral",
        )
        out["EXP_entryPrice"] = out["close"].where(out["EXP_longSignal"] | out["EXP_shortSignal"])
        out["EXP_stopPrice"] = np.where(out["EXP_longSignal"], out["low"] - out["atr"] * 0.18, np.where(out["EXP_shortSignal"], out["high"] + out["atr"] * 0.18, np.nan))
        return out
