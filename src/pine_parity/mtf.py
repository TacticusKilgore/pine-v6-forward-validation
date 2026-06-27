from __future__ import annotations

from typing import Optional
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
    ltf = df_ltf.copy().sort_values(ts_col).reset_index(drop=True)
    htf = df_htf.copy().sort_values(ts_col).reset_index(drop=True)
    if columns is None:
        columns = [c for c in htf.columns if c != ts_col]
    if confirmed_only:
        value_cols = [c for c in htf.columns if c != ts_col]
        shifted = htf.copy()
        shifted[value_cols] = shifted[value_cols].shift(1)
        htf = shifted.dropna(subset=value_cols)
    reduced = htf[[ts_col] + columns]
    merged = pd.merge_asof(ltf, reduced, on=ts_col, direction="backward", suffixes=("", suffix))
    return merged.rename(columns={c: f"{c}{suffix}" for c in columns if c in merged.columns})


def resample_to_htf(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return resample_ohlcv(df, rule)
