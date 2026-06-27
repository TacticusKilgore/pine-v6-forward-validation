#!/usr/bin/env python3
"""
CLI for forward shadow mode.

Forward shadowing allows a strategy to be monitored on recent data without
executing real trades. It generates signals on the latest dataset, then
computes the realised forward returns for specified horizons where possible
and leaves others as open. The output can be used to assess the near‑term
behaviour of the strategy and to calibrate parameters before live trading.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Dict

import pandas as pd

from src.data.csv_loader import load_csv
from src.engine.signal_engine import run_strategy
from src.engine.trade_engine import evaluate_multiple_horizons


def forward_shadow(
    df: pd.DataFrame,
    strategy_name: str,
    config: Dict[str, any],
    horizons: List[int],
) -> pd.DataFrame:
    """Compute forward shadow results for a strategy on recent data.

    Signals are generated on the entire dataset. For each signal, the
    forward return is calculated after the specified horizon bars if
    sufficient data exists; otherwise the result is marked as open (NaN).

    Args:
        df: OHLCV DataFrame.
        strategy_name: Name of the strategy to execute.
        config: Strategy configuration.
        horizons: List of horizon lengths in bars.

    Returns:
        DataFrame with original data, signals and forward returns labelled
        ``result_<h>`` for each horizon ``h``. A status column indicates
        whether the horizon result is available ("closed") or pending ("open").
    """
    # Run strategy
    signals = run_strategy(df, strategy_name, config)
    # Evaluate forward returns
    evaluated = evaluate_multiple_horizons(signals, horizons)
    # Rename forward return columns to result_<h>
    result_df = evaluated.copy()
    for h in horizons:
        col_name = f"fwd_return_{h}"
        result_name = f"result_{h}"
        if col_name in result_df.columns:
            result_df[result_name] = result_df[col_name]
            result_df.drop(columns=[col_name], inplace=True)
    # Determine status per horizon: closed if not NaN, else open
    for h in horizons:
        status_col = f"status_{h}"
        res_col = f"result_{h}"
        result_df[status_col] = result_df[res_col].apply(lambda x: "closed" if pd.notna(x) else "open")
    return result_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Run forward shadow mode for a strategy")
    parser.add_argument("--data", required=True, help="Path to CSV file with OHLCV data")
    parser.add_argument("--strategy", required=True, help="Strategy name (amlrx, iax, ivsf, elc)")
    parser.add_argument("--config", help="Optional JSON string of strategy parameters")
    parser.add_argument("--horizons", nargs="+", type=int, default=[3, 5, 10], help="Horizon bars for forward shadow")
    parser.add_argument("--out", required=True, help="Output CSV file path for forward shadow results")
    args = parser.parse_args()
    # Load data
    df = load_csv(args.data)
    # Parse config JSON if provided
    import json
    config: Dict[str, any] = {}
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid config JSON: {exc}")
    # Compute forward shadow
    result_df = forward_shadow(df, args.strategy, config, args.horizons)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(out_path, index=False)
    print(f"Forward shadow results saved to {out_path}")


if __name__ == "__main__":
    main()