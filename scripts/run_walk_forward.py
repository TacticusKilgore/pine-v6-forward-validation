#!/usr/bin/env python
"""
Command‑line interface for performing a simple walk‑forward style forward return evaluation.

This script ties together data loading, configuration parsing, signal generation and
forward return evaluation. Given a CSV file containing OHLCV data, a strategy name
and a YAML configuration, it will compute signals for each bar, evaluate forward
returns over multiple horizons and produce a Markdown report summarising the
results.

Usage example:

```
python scripts/run_walk_forward.py \
  --data data/raw/BTCUSDT_5m.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml \
  --out reports/walk_forward/BTCUSDT_amlrx.md \
  --horizons 3 5 10
```

The ``--horizons`` argument accepts one or more integers indicating how many bars
ahead the forward return should be computed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import pandas as pd

from src.data.config_loader import load_yaml_config
from src.engine.signal_engine import run_strategy
from src.engine.trade_engine import evaluate_multiple_horizons, summarize_forward_returns
from src.reports.summary_report import write_summary_report


def parse_arguments() -> argparse.Namespace:
    """Parse command‑line arguments for the walk forward script."""
    parser = argparse.ArgumentParser(
        description="Run forward return evaluation for a given strategy on OHLCV data"
    )
    parser.add_argument(
        "--data",
        dest="data_path",
        required=True,
        help="Path to the input CSV containing OHLCV data",
    )
    parser.add_argument(
        "--strategy",
        dest="strategy",
        required=True,
        help="Name of the strategy to run (e.g. amlrx, iax, ivsf, elc)",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        required=True,
        help="Path to the YAML configuration file for the strategy",
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        required=True,
        help="Path to the output Markdown report",
    )
    parser.add_argument(
        "--horizons",
        dest="horizons",
        required=True,
        nargs="+",
        type=int,
        help="One or more integers specifying the number of bars ahead for forward returns",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    data_file = Path(args.data_path)
    config_file = Path(args.config_path)
    out_file = Path(args.out_path)
    horizons: List[int] = args.horizons

    # Load OHLCV data
    try:
        df = pd.read_csv(data_file)
    except Exception as e:
        raise SystemExit(f"Error reading CSV {data_file}: {e}")

    # Load configuration
    try:
        config = load_yaml_config(config_file)
    except Exception as e:
        raise SystemExit(str(e))

    # Run strategy to compute signals and scores
    try:
        result_df = run_strategy(df, args.strategy, config)
    except Exception as e:
        raise SystemExit(f"Error running strategy {args.strategy}: {e}")

    # Evaluate forward returns for each horizon
    returns_df = evaluate_multiple_horizons(result_df, horizons)
    summary = summarize_forward_returns(returns_df, horizons)

    # Write the summary report
    try:
        write_summary_report(summary, out_file)
    except Exception as e:
        raise SystemExit(f"Error writing report to {out_file}: {e}")

    print(f"Report written to {out_file}")


if __name__ == "__main__":  # pragma: no cover
    main()