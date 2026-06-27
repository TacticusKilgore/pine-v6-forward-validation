from __future__ import annotations

import pandas as pd


def ensure_vectorbt_available():
    try:
        import vectorbt as vbt  # type: ignore
    except ImportError as exc:
        raise ImportError("Install vectorbt to use this optimizer") from exc
    return vbt


def run_vectorbt_portfolio(close: pd.Series, entries: pd.Series, exits: pd.Series, fees: float = 0.0006):
    vbt = ensure_vectorbt_available()
    return vbt.Portfolio.from_signals(close=close, entries=entries, exits=exits, fees=fees)
