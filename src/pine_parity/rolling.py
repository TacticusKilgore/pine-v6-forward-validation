from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd


def pine_sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=int(length), min_periods=int(length)).mean()


def pine_ema(series: pd.Series, length: int) -> pd.Series:
    if length <= 0:
        raise ValueError("length must be positive")
    alpha = 2 / (length + 1)
    out = series.astype(float).copy()
    out[:] = np.nan
    first = series.first_valid_index()
    if first is None:
        return out
    out.at[first] = float(series.at[first])
    start = series.index.get_loc(first) + 1
    for i in range(start, len(series)):
        out.iat[i] = alpha * float(series.iat[i]) + (1 - alpha) * float(out.iat[i - 1])
    return out


def pine_rma(series: pd.Series, length: int) -> pd.Series:
    n = int(length)
    if n <= 0:
        raise ValueError("length must be positive")
    out = series.astype(float).copy()
    out[:] = np.nan
    for i in range(len(series)):
        if i + 1 < n:
            continue
        if i + 1 == n:
            out.iat[i] = float(series.iloc[:n].mean())
        else:
            out.iat[i] = (float(out.iat[i - 1]) * (n - 1) + float(series.iat[i])) / n
    return out


def rolling_highest(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=int(length), min_periods=int(length)).max()


def rolling_lowest(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=int(length), min_periods=int(length)).min()


def rolling_sum(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=int(length), min_periods=int(length)).sum()


def barssince(condition: pd.Series) -> pd.Series:
    out = pd.Series(index=condition.index, dtype=float)
    last_true: Optional[int] = None
    for i, cond in enumerate(condition):
        if bool(cond):
            last_true = i
            out.iat[i] = 0
        else:
            out.iat[i] = np.nan if last_true is None else i - last_true
    return out
