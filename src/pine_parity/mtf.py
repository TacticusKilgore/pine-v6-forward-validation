from __future__ import annotations

from collections.abc import Sequence
import pandas as pd


def align_higher_timeframe(ltf: pd.DataFrame, htf: pd.DataFrame, value_cols: Sequence[str], confirmed_only: bool = True) -> pd.DataFrame:
    left = ltf.copy().sort_values("timestamp")
    right = htf[["timestamp", *value_cols]].copy().sort_values("timestamp")
    right = right.astype({col: "float64" for col in value_cols})
    if confirmed_only:
        right.loc[:, value_cols] = right.loc[:, value_cols].shift(1)
    out = pd.merge_asof(left, right, on="timestamp", direction="backward")
    return out.rename(columns={col: f"{col}_htf" for col in value_cols})
