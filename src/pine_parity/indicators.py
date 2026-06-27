from __future__ import annotations

import numpy as np
import pandas as pd

from src.pine_parity.rolling import pine_rma


def hlc3(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return (high + low + close) / 3.0


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    high_low = high - low
    high_prev = (high - prev_close).abs()
    low_prev = (low - prev_close).abs()
    tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)
    if len(tr):
        tr.iloc[0] = high.iloc[0] - low.iloc[0]
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> pd.Series:
    return pine_rma(true_range(high, low, close), int(length))


def vwap_sessionless(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    typical_price = hlc3(high, low, close)
    cumulative_volume = volume.cumsum().replace(0, np.nan)
    return (typical_price * volume).cumsum() / cumulative_volume


def body_size(open: pd.Series, close: pd.Series) -> pd.Series:
    return (close - open).abs()


def upper_wick(open: pd.Series, high: pd.Series, close: pd.Series) -> pd.Series:
    return high - np.maximum(open, close)


def lower_wick(open: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return np.minimum(open, close) - low


def close_location(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    candle_range = (high - low).replace(0, np.nan)
    return (close - low) / candle_range


def body_efficiency(high: pd.Series, low: pd.Series, open: pd.Series, close: pd.Series) -> pd.Series:
    candle_range = (high - low).replace(0, np.nan)
    return body_size(open, close) / candle_range
