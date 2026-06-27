#!/usr/bin/env python3
"""
CLI entry point for parameter optimisation.

This script performs a brute‑force grid search over a discrete parameter
space for a specified strategy. It loads OHLCV data from a CSV file,
executes the strategy for each parameter combination, computes forward
returns across the given horizons and evaluates an objective function to
select the best configuration. Results are written to a CSV file and
optionally printed to stdout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.data.csv_loader import load_csv
from src.optimizers.grid_search import grid_search


def parse_param_grid(param_str: str) -> Dict[str, List[Any]]:
    """Parse a JSON string or file containing the parameter grid.

    The parameter grid must be a dictionary where each key is a parameter
    name and each value is a list of candidate values. For example:

    ``{"atr_length": [10, 14, 20], "value_mid_length": [10, 20]}``

    Args:
        param_str: JSON string or path to a JSON/YAML file.

    Returns:
        A dictionary mapping parameter names to lists of values.
    """
    # If param_str is a path to a file, read it
    path = Path(param_str)
    if path.exists():
        text = path.read_text()
    else:
        text = param_str
    try:
        grid = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid parameter grid JSON: {exc}") from exc
    if not isinstance(grid, dict):
        raise ValueError("Parameter grid must be a JSON object with parameter names and value lists")
    # Ensure each value is a list
    for k, v in grid.items():
        if not isinstance(v, list):
            grid[k] = [v]
    return grid


def main() -> None:
    parser = argparse.ArgumentParser(description="Run grid search optimisation for a trading strategy")
    parser.add_argument("--data", required=True, help="Path to CSV file containing OHLCV data")
    parser.add_argument("--strategy", required=True, help="Name of the strategy (amlrx, iax, ivsf, elc)")
    parser.add_argument("--param_grid", required=True, help="JSON string or file path specifying parameter grid")
    parser.add_argument("--horizons", nargs="+", type=int, default=[3, 5, 10], help="Forward return horizons")
    parser.add_argument("--out", required=True, help="Path to output CSV file for optimisation results")
    args = parser.parse_args()

    df = load_csv(args.data)
    param_grid = parse_param_grid(args.param_grid)
    best_params, results_df = grid_search(df, args.strategy, param_grid, args.horizons)
    # Write results to CSV; summary column (nested objects) is dropped
    out_path = Path(args.out)
    # Flatten summary for storage: store summary as JSON string
    df_to_save = results_df.copy()
    df_to_save["summary_json"] = df_to_save["summary"].apply(lambda x: json.dumps(x, default=str))
    df_to_save = df_to_save.drop(columns=["summary"]) if "summary" in df_to_save.columns else df_to_save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_to_save.to_csv(out_path, index=False)
    # Print best parameters
    print("Best parameters:")
    print(best_params)


if __name__ == "__main__":
    main()