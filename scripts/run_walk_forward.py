#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import yaml

from src.data.csv_loader import load_ohlcv_csv
from src.engine.signal_engine import run_signal_engine
from src.engine.walk_forward import build_walk_forward_windows, evaluate_frozen_walk_forward
from src.reports.json_report import write_json_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--train-days", type=int, default=45)
    parser.add_argument("--validation-days", type=int, default=15)
    parser.add_argument("--forward-days", type=int, default=10)
    parser.add_argument("--step-days", type=int, default=10)
    parser.add_argument("--report-out", default="reports/walk_forward/latest_walk_forward.json")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    df = load_ohlcv_csv(args.data)
    windows = build_walk_forward_windows(df.index, args.train_days, args.validation_days, args.forward_days, args.step_days)
    print(f"windows={len(windows)}")

    def signal_fn(frame, frozen_params):
        _ = frozen_params
        return run_signal_engine(frame, args.strategy, cfg)

    results = evaluate_frozen_walk_forward(df, windows, signal_fn)
    payload = {"strategy": args.strategy, "windows": []}
    for i, result in enumerate(results, start=1):
        window = result.window
        metrics = result.forward_metrics
        print(
            f"window={i} forward={window.forward_start}..{window.forward_end} "
            f"trades={metrics['trade_count']} expectancy={metrics['expectancy_r']:.4f} "
            f"robust_score={result.robust_score:.2f}"
        )
        payload["windows"].append(result)
    report_path = write_json_report(payload, args.report_out)
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
