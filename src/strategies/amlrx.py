from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from src.pine_parity.indicators import add_common_features
from src.pine_parity.rolling import pine_sma


@dataclass(frozen=True)
class AMLRXParams:
    atr_len: int = 14
    value_lookback: int = 48
    stability_lookback: int = 24
    zone_atr_mult: float = 0.75
    displacement_atr_min: float = 0.35
    failed_acceptance_bars: int = 5
    reentry_window_bars: int = 8
    min_score: float = 60.0
    cooldown_bars: int = 8


class AMLRXStrategy:
    """Auction Migration Lag Re-Entry after Failed Displacement.

    OHLCV-only mirror suitable for Pine-v6 parity development. It detects price leaving a
    local value zone, failing to accept outside, then re-entering the previous value structure.
    """

    name = "amlrx"

    def __init__(self, params: AMLRXParams | None = None) -> None:
        self.params = params or AMLRXParams()

    @classmethod
    def from_config(cls, cfg: dict) -> "AMLRXStrategy":
        params = AMLRXParams(**cfg.get("params", {}))
        return cls(params)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = add_common_features(df, atr_len=p.atr_len)
        out["value_mid"] = pine_sma(out["hlc3"], p.value_lookback)
        range_raw = out["high"] - out["low"]
        range_stability = 1.0 / (1.0 + (range_raw / out["atr"]).rolling(p.stability_lookback, min_periods=p.stability_lookback).std())
        out["value_width"] = out["atr"] * p.zone_atr_mult * range_stability.clip(lower=0.35, upper=1.25)
        out["zone_upper"] = out["value_mid"] + out["value_width"]
        out["zone_lower"] = out["value_mid"] - out["value_width"]

        outside_up = out["close"] > out["zone_upper"] + out["atr"] * p.displacement_atr_min
        outside_down = out["close"] < out["zone_lower"] - out["atr"] * p.displacement_atr_min
        inside = (out["close"] <= out["zone_upper"]) & (out["close"] >= out["zone_lower"])

        last_up_age = _bars_since_last_true(outside_up)
        last_down_age = _bars_since_last_true(outside_down)
        recent_up_displacement = last_up_age.between(1, p.reentry_window_bars)
        recent_down_displacement = last_down_age.between(1, p.reentry_window_bars)

        accept_up = out["close"].rolling(p.failed_acceptance_bars).min() > out["zone_upper"]
        accept_down = out["close"].rolling(p.failed_acceptance_bars).max() < out["zone_lower"]
        failed_up_acceptance = recent_up_displacement & (~accept_up)
        failed_down_acceptance = recent_down_displacement & (~accept_down)

        quality = np.select(
            [inside & failed_up_acceptance, inside & failed_down_acceptance],
            [
                50 + 25 * (out["upper_wick"].fillna(0)) + 25 * (out["vol_ratio"].fillna(1).clip(0, 3) / 3),
                50 + 25 * (out["lower_wick"].fillna(0)) + 25 * (out["vol_ratio"].fillna(1).clip(0, 3) / 3),
            ],
            default=0.0,
        )
        out["EXP_score"] = pd.Series(quality, index=out.index).clip(0, 100)
        out["EXP_shortSignal"] = inside & failed_up_acceptance & (out["EXP_score"] >= p.min_score)
        out["EXP_longSignal"] = inside & failed_down_acceptance & (out["EXP_score"] >= p.min_score)
        out["EXP_state"] = np.select(
            [out["EXP_longSignal"], out["EXP_shortSignal"], outside_up, outside_down],
            ["Active Long", "Active Short", "Armed Short", "Armed Long"],
            default="Neutral",
        )
        out["EXP_entryPrice"] = out["close"].where(out["EXP_longSignal"] | out["EXP_shortSignal"])
        out["EXP_stopPrice"] = np.where(
            out["EXP_longSignal"],
            out["low"] - out["atr"] * 0.65,
            np.where(out["EXP_shortSignal"], out["high"] + out["atr"] * 0.65, np.nan),
        )
        risk = (out["EXP_entryPrice"] - out["EXP_stopPrice"]).abs()
        out["EXP_tp1"] = np.where(
            out["EXP_longSignal"],
            out["EXP_entryPrice"] + risk * 1.8,
            np.where(out["EXP_shortSignal"], out["EXP_entryPrice"] - risk * 1.8, np.nan),
        )
        return out


def _bars_since_last_true(condition: pd.Series) -> pd.Series:
    age = []
    last_idx = None
    for i, flag in enumerate(condition.fillna(False).astype(bool).to_numpy()):
        if flag:
            last_idx = i
            age.append(0)
        else:
            age.append(np.nan if last_idx is None else i - last_idx)
    return pd.Series(age, index=condition.index, dtype="float64")
