from __future__ import annotations

import numpy as np
import pandas as pd

from .rolling import pine_ema, pine_rma, pine_sma


def hlc3(df: pd.DataFrame) -> pd.Series:
    return (df["high"] + df["low"] + df["close"]) / 3.0


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    ranges = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    return pine_rma(true_range(df), length)


def ema(series: pd.Series, length: int) -> pd.Series:
    return pine_ema(series, length)


def sma(series: pd.Series, length: int) -> pd.Series:
    return pine_sma(series, length)


def rolling_vwap(df: pd.DataFrame, length: int) -> pd.Series:
    typical = hlc3(df)
    pv = typical * df["volume"]
    vol_sum = df["volume"].rolling(length, min_periods=length).sum()
    pv_sum = pv.rolling(length, min_periods=length).sum()
    return pv_sum / vol_sum.replace(0, np.nan)


def anchored_daily_vwap(df: pd.DataFrame) -> pd.Series:
    typical = hlc3(df)
    dates = df.index.tz_convert("UTC").date if df.index.tz is not None else df.index.date
    pv = typical * df["volume"]
    cum_pv = pv.groupby(dates).cumsum()
    cum_vol = df["volume"].groupby(dates).cumsum()
    return cum_pv / cum_vol.replace(0, np.nan)


def body_size(df: pd.DataFrame) -> pd.Series:
    return (df["close"] - df["open"]).abs()


def candle_range(df: pd.DataFrame) -> pd.Series:
    return (df["high"] - df["low"]).replace(0, np.nan)


def body_efficiency(df: pd.DataFrame) -> pd.Series:
    return body_size(df) / candle_range(df)


def close_location(df: pd.DataFrame) -> pd.Series:
    return (df["close"] - df["low"]) / candle_range(df)


def upper_wick_ratio(df: pd.DataFrame) -> pd.Series:
    upper = df["high"] - pd.concat([df["open"], df["close"]], axis=1).max(axis=1)
    return upper / candle_range(df)


def lower_wick_ratio(df: pd.DataFrame) -> pd.Series:
    lower = pd.concat([df["open"], df["close"]], axis=1).min(axis=1) - df["low"]
    return lower / candle_range(df)


def add_common_features(df: pd.DataFrame, atr_len: int = 14, volume_len: int = 20) -> pd.DataFrame:
    out = df.copy()
    out["hlc3"] = hlc3(out)
    out["atr"] = atr(out, atr_len)
    out["ema20"] = ema(out["close"], 20)
    out["ema200"] = ema(out["close"], 200)
    out["vwap_d"] = anchored_daily_vwap(out)
    out["vol_sma"] = sma(out["volume"], volume_len)
    out["vol_ratio"] = out["volume"] / out["vol_sma"].replace(0, np.nan)
    out["body_eff"] = body_efficiency(out)
    out["close_loc"] = close_location(out)
    out["upper_wick"] = upper_wick_ratio(out)
    out["lower_wick"] = lower_wick_ratio(out)
    return out
