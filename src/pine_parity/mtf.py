from __future__ import annotations

from typing import Optional, Sequence
import pandas as pd

from src.data.resampler import resample_ohlcv


def align_htf_to_ltf(
    df_ltf: pd.DataFrame,
    df_htf: pd.DataFrame,
    *,
    confirmed_only: bool = True,
    ts_col: str = "timestamp",
    suffix: str = "_htf",
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Align higher-timeframe values onto lower-timeframe rows.

    Default behavior is confirmed-bar safe: HTF value columns are shifted by one
    HTF row before asof-merge, so the current unfinished HTF candle is never used.
    """
    ltf = df_ltf.copy().sort_values(ts_col).reset_index(drop=True)
    htf = df_htf.copy().sort_values(ts_col).reset_index(drop=True)
    if columns is None:
        columns = [c for c in htf.columns if c != ts_col]
    if confirmed_only:
        value_cols = [c for c in htf.columns if c != ts_col]
        shifted = htf.copy()
        shifted[value_cols] = shifted[value_cols].shift(1)
        htf = shifted.dropna(subset=value_cols, how="all")
    reduced = htf[[ts_col] + list(columns)]
    merged = pd.merge_asof(ltf, reduced, on=ts_col, direction="backward", suffixes=("", suffix))
    return merged.rename(columns={c: f"{c}{suffix}" for c in columns if c in merged.columns})


def align_higher_timeframe(
    ltf: pd.DataFrame,
    htf: pd.DataFrame,
    value_cols: Sequence[str],
    confirmed_only: bool = True,
) -> pd.DataFrame:
    """Backward-compatible alias used by the original scaffold tests."""
    return align_htf_to_ltf(
        ltf,
        htf,
        confirmed_only=confirmed_only,
        ts_col="timestamp",
        suffix="_htf",
        columns=list(value_cols),
    )


def resample_to_htf(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return resample_ohlcv(df, rule)
