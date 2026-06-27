from __future__ import annotations

import pandas as pd


def evaluate_forward_returns(df: pd.DataFrame, horizon_bars: int = 10) -> pd.DataFrame:
    out = df.copy()
    side = out["signal"].astype(int)
    entry = out["open"].shift(-1)
    exit_price = out["close"].shift(-horizon_bars)
    out["forward_return"] = ((exit_price - entry) / entry) * side
    return out
