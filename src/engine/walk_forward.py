"""
Walk‑forward analysis engine.

This module implements a basic walk‑forward validation framework. It splits
chronological data into sequential train and test windows and evaluates a
strategy on each test window using a fixed configuration. The train window
can be used for parameter estimation or simple pre‑calculation, but no
optimisation across train and test is performed here. This implementation
ensures there is no information leakage between windows by strictly using
past data to inform subsequent periods.

Key functions:

* ``chronological_windows``: Generate tuples of (train_start, train_end,
  test_start, test_end) indices covering the dataset.
* ``run_walk_forward``: Execute the walk‑forward evaluation for a given
  strategy, producing a list of results per window.
* ``summarize_walk_forward``: Aggregate per‑window statistics into a
  summary DataFrame.

The functions intentionally accept indices rather than timestamps to
accommodate non‑date indices. If the DataFrame index is a DatetimeIndex,
windows correspond to contiguous time slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import pandas as pd

from src.engine.signal_engine import run_strategy
from src.engine.trade_engine import evaluate_multiple_horizons, summarize_forward_returns


@dataclass
class WindowSpec:
    """Definition of a train/test window within the dataset."""

    train_start: int
    train_end: int
    test_start: int
    test_end: int


def chronological_windows(
    length: int,
    train_size: int,
    test_size: int,
    step_size: int,
) -> List[WindowSpec]:
    """Compute sequential train/test windows over a dataset of given length."""
    windows = []
    start = 0
    while True:
        train_start = start
        train_end = train_start + train_size
        test_start = train_end
        test_end = test_start + test_size
        if test_end > length:
            break
        windows.append(WindowSpec(train_start, train_end, test_start, test_end))
        start += step_size
    return windows


def run_walk_forward(
    df: pd.DataFrame,
    strategy_name: str,
    config: Dict[str, Any],
    horizons: List[int],
    train_size: int,
    test_size: int,
    step_size: int,
    cost_params: Dict[str, float] | None = None,
    symbol: str = "",
    timeframe: str = "",
) -> List[Dict[str, Any]]:
    """Execute walk‑forward evaluation."""
    results: List[Dict[str, Any]] = []
    n = len(df)
    windows = chronological_windows(n, train_size, test_size, step_size)
    for idx, win in enumerate(windows):
        test_df = df.iloc[win.test_start : win.test_end].copy().reset_index(drop=True)
        signals = run_strategy(test_df, strategy_name, config)
        evaluated = evaluate_multiple_horizons(signals, horizons)
        summary = summarize_forward_returns(evaluated, horizons)
        for s in summary:
            s["window_id"] = idx
            s["test_start_index"] = win.test_start
            s["test_end_index"] = win.test_end
            s["train_start_index"] = win.train_start
            s["train_end_index"] = win.train_end
            s["symbol"] = symbol
            s["timeframe"] = timeframe
            s["strategy"] = strategy_name
        results.extend(summary)
    return results


def summarize_walk_forward(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """Aggregate walk‑forward results into a DataFrame."""
    return pd.DataFrame(results)