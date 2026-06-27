"""
Grid search optimiser for trading strategy parameters.
"""

from __future__ import annotations

from itertools import product
from typing import Dict, Any, List, Callable, Tuple

import numpy as np
import pandas as pd

from src.engine.signal_engine import run_strategy
from src.engine.trade_engine import evaluate_multiple_horizons, summarize_forward_returns


def default_objective(summary: List[Dict[str, Any]]) -> float:
    if not summary:
        return float("-inf")
    mean_returns = [s.get("mean_forward_return", 0) or 0 for s in summary]
    win_rates = [s.get("win_rate", 0) or 0 for s in summary]
    trade_counts = [s.get("signals_total", 0) or 0 for s in summary]
    avg_return = np.mean(mean_returns) if mean_returns else 0.0
    avg_win_rate = np.mean(win_rates) if win_rates else 0.0
    avg_trades = np.mean(trade_counts) if trade_counts else 0.0
    return float(avg_return * 0.6 + avg_win_rate * 0.3 + (avg_trades / 100.0) * 0.1)


def grid_search(
    df: pd.DataFrame,
    strategy_name: str,
    param_grid: Dict[str, List[Any]],
    horizons: List[int],
    objective: Callable[[List[Dict[str, Any]]], float] = default_objective,
    max_candidates: int | None = None,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]
    combos = list(product(*values))
    if max_candidates is not None:
        combos = combos[:max_candidates]
    results = []
    best_score = float("-inf")
    best_params: Dict[str, Any] = {}
    for combo in combos:
        params = {k: v for k, v in zip(keys, combo)}
        signals = run_strategy(df, strategy_name, params)
        evaluated = evaluate_multiple_horizons(signals, horizons)
        summary = summarize_forward_returns(evaluated, horizons)
        score = objective(summary)
        results.append({**params, "score": score, "summary": summary})
        if score > best_score:
            best_score = score
            best_params = params
    return best_params, pd.DataFrame(results)