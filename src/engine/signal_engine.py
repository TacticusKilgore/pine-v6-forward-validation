from __future__ import annotations

import pandas as pd

from src.strategies.registry import build_strategy


def run_signal_engine(df: pd.DataFrame, strategy_name: str, config: dict) -> pd.DataFrame:
    strategy = build_strategy(strategy_name, config)
    return strategy.run(df)
