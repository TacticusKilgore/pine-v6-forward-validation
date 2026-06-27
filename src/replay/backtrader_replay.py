from __future__ import annotations

import pandas as pd


def ensure_backtrader_available():
    try:
        import backtrader as bt  # type: ignore
    except ImportError as exc:
        raise ImportError("Install backtrader to use replay adapter") from exc
    return bt


def dataframe_to_backtrader_feed(df: pd.DataFrame):
    bt = ensure_backtrader_available()
    return bt.feeds.PandasData(dataname=df)
