from __future__ import annotations

import pandas as pd

from src.data.resampler import resample_ohlcv


def confirmed_htf_series(
    ltf_df: pd.DataFrame,
    htf_timeframe: str,
    value_fn,
    shift_confirmed: bool = True,
) -> pd.Series:
    """Map confirmed higher-timeframe values to lower-timeframe bars.

    `value_fn` receives the resampled HTF DataFrame and returns a Series indexed by HTF close time.
    When `shift_confirmed=True`, the current HTF candle is not visible to the LTF bars inside it.
    """
    if not isinstance(ltf_df.index, pd.DatetimeIndex):
        raise TypeError("ltf_df must be indexed by timestamp")
    htf = resample_ohlcv(ltf_df, htf_timeframe)
    htf_values = value_fn(htf)
    if shift_confirmed:
        htf_values = htf_values.shift(1)
    aligned = htf_values.reindex(ltf_df.index, method="ffill")
    return aligned


def assert_no_future_htf_leak(ltf_df: pd.DataFrame, aligned: pd.Series, htf_timeframe: str) -> None:
    """Basic structural check for HTF mapping.

    The function verifies index equality and avoids silent misalignment. It cannot prove semantic
    correctness of a custom value function; parity tests must cover that separately.
    """
    if not aligned.index.equals(ltf_df.index):
        raise AssertionError(f"Aligned HTF series index mismatch for {htf_timeframe}")
    if aligned.index.has_duplicates:
        raise AssertionError("Aligned HTF series contains duplicate timestamps")
