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
from src.pine_parity.future_leak import assert_prefix_stability

DEFAULT_COLUMNS = [
    "EXP_state",
    "EXP_score",
    "EXP_longSignal",
    "EXP_shortSignal",
    "EXP_entryPrice",
    "EXP_stopPrice",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Pine-parity strategy output for prefix stability / future leak.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--warmup-bars", type=int, default=250)
    parser.add_argument("--columns", nargs="*", default=DEFAULT_COLUMNS)
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    df = load_ohlcv_csv(args.data)
    report = assert_prefix_stability(
        lambda frame: run_signal_engine(frame, args.strategy, cfg),
        df,
        args.columns,
        warmup_bars=args.warmup_bars,
    )
    print(f"passed={report.passed} checked_cutoffs={report.checked_cutoffs} mismatches={len(report.mismatches)}")
    for mismatch in report.mismatches[:20]:
        print(
            f"cutoff={mismatch.cutoff} ts={mismatch.timestamp} column={mismatch.column} "
            f"full={mismatch.full_value} prefix={mismatch.prefix_value}"
        )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
