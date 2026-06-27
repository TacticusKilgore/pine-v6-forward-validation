from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any
import pandas as pd

from src.engine.robustness import trade_metrics, robust_score
from src.engine.trade_engine import simulate_trades


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    validation_start: pd.Timestamp
    validation_end: pd.Timestamp
    forward_start: pd.Timestamp
    forward_end: pd.Timestamp


@dataclass(frozen=True)
class WalkForwardResult:
    window: WalkForwardWindow
    train_metrics: dict[str, float]
    validation_metrics: dict[str, float]
    forward_metrics: dict[str, float]
    selected_params: dict[str, Any]
    robust_score: float


def build_walk_forward_windows(
    index: pd.DatetimeIndex,
    train_days: int,
    validation_days: int,
    forward_days: int,
    step_days: int,
) -> list[WalkForwardWindow]:
    if len(index) == 0:
        return []
    if min(train_days, validation_days, forward_days, step_days) <= 0:
        raise ValueError("walk-forward day parameters must be positive")
    start = index.min()
    end = index.max()
    windows: list[WalkForwardWindow] = []
    cursor = start
    while True:
        train_start = cursor
        train_end = train_start + pd.Timedelta(days=train_days)
        validation_start = train_end
        validation_end = validation_start + pd.Timedelta(days=validation_days)
        forward_start = validation_end
        forward_end = forward_start + pd.Timedelta(days=forward_days)
        if forward_end > end:
            break
        windows.append(
            WalkForwardWindow(
                train_start=train_start,
                train_end=train_end,
                validation_start=validation_start,
                validation_end=validation_end,
                forward_start=forward_start,
                forward_end=forward_end,
            )
        )
        cursor = cursor + pd.Timedelta(days=step_days)
    return windows


def slice_window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return df.loc[(df.index >= start) & (df.index < end)].copy()


def evaluate_frozen_walk_forward(
    df: pd.DataFrame,
    windows: list[WalkForwardWindow],
    signal_fn: Callable[[pd.DataFrame, dict[str, Any]], pd.DataFrame],
    selected_params_fn: Callable[[pd.DataFrame, pd.DataFrame], dict[str, Any]] | None = None,
) -> list[WalkForwardResult]:
    """Evaluate walk-forward windows with parameters frozen before the forward slice.

    `selected_params_fn` receives train and validation data only. It must not inspect the
    forward window. If omitted, an empty immutable parameter set is used.
    """
    results: list[WalkForwardResult] = []
    for window in windows:
        train_df = slice_window(df, window.train_start, window.train_end)
        validation_df = slice_window(df, window.validation_start, window.validation_end)
        forward_df = slice_window(df, window.forward_start, window.forward_end)
        selected_params = selected_params_fn(train_df, validation_df) if selected_params_fn else {}

        train_trades = simulate_trades(signal_fn(train_df, selected_params))
        validation_trades = simulate_trades(signal_fn(validation_df, selected_params))
        forward_trades = simulate_trades(signal_fn(forward_df, selected_params))
        fwd_metrics = trade_metrics(forward_trades)
        results.append(
            WalkForwardResult(
                window=window,
                train_metrics=trade_metrics(train_trades),
                validation_metrics=trade_metrics(validation_trades),
                forward_metrics=fwd_metrics,
                selected_params=selected_params,
                robust_score=robust_score(fwd_metrics),
            )
        )
    return results
