from __future__ import annotations

from importlib import import_module
import pandas as pd

MODULES = {"amlrx": "src.strategies.amlrx", "iax": "src.strategies.iax", "ivsf": "src.strategies.ivsf", "elc": "src.strategies.elc"}


def run_strategy(df: pd.DataFrame, strategy: str, config: dict | None = None) -> pd.DataFrame:
    if strategy not in MODULES:
        raise ValueError(f"Unknown strategy: {strategy}")
    return import_module(MODULES[strategy]).generate_signals(df, config)
