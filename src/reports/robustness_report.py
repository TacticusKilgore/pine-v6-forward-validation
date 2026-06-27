from __future__ import annotations

import pandas as pd


def summarize_by_side(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    return trades.groupby("side")["net_r"].agg(["count", "mean", "median", "sum"])
