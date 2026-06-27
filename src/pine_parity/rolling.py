from __future__ import annotations

import pandas as pd


def pine_sma(series: pd.Series, length: int) -> pd.Series:
    if length <= 0:
        raise ValueError("length must be positive")
    return series.rolling(length, min_periods=length).mean()


def pine_ema(series: pd.Series, length: int) -> pd.Series:
    if length <= 0:
        raise ValueError("length must be positive")
    return series.ewm(span=length, adjust=False, min_periods=length).mean()


def pine_rma(series: pd.Series, length: int) -> pd.Series:
    """TradingView-like RMA/Wilder smoothing.

    Pine's ta.rma starts with an SMA seed once enough non-NaN values exist.
    """
    if length <= 0:
        raise ValueError("length must be positive")
    values = series.astype(float)
    out = pd.Series(index=series.index, dtype="float64")
    valid = values.dropna()
    if len(valid) < length:
        return out

    seed_idx = valid.index[length - 1]
    seed = valid.iloc[:length].mean()
    out.loc[seed_idx] = seed
    alpha = 1.0 / length
    prev = seed
    started = False
    for idx, value in values.items():
        if idx == seed_idx:
            started = True
            continue
        if not started or pd.isna(value):
            continue
        prev = alpha * value + (1.0 - alpha) * prev
        out.loc[idx] = prev
    return out


def bars_since(condition: pd.Series) -> pd.Series:
    """Return bars since condition was true, Pine-like.

    NaN before first true event.
    """
    out = []
    count: int | None = None
    for flag in condition.fillna(False).astype(bool):
        if flag:
            count = 0
        elif count is not None:
            count += 1
        out.append(float("nan") if count is None else count)
    return pd.Series(out, index=condition.index, dtype="float64")
