#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.csv_loader import load_ohlcv_csv
from src.engine.signal_engine import run_signal_engine
from src.engine.trade_engine import simulate_trades
from src.engine.robustness import trade_metrics, robust_score
from src.optimizers.grid_search import grid_search


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--strategy", default="amlrx")
    parser.add_argument("--config", default="configs/amlrx_v0_1.yaml")
    args = parser.parse_args()

    base_cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    df = load_ohlcv_csv(args.data)

    grid = {
        "min_score": [55, 60, 65, 70],
        "reentry_window_bars": [5, 8, 12],
        "zone_atr_mult": [0.60, 0.75, 0.90],
    }

    def objective(params):
        cfg = dict(base_cfg)
        cfg["params"] = {**base_cfg.get("params", {}), **params}
        signals = run_signal_engine(df, args.strategy, cfg)
        trades = simulate_trades(signals)
        metrics = trade_metrics(trades)
        return {**metrics, "robust_score": robust_score(metrics)}

    result = grid_search(grid, objective).sort_values("robust_score", ascending=False)
    print(result.head(20).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
