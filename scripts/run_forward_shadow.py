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


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline shadow-forward runner over appended OHLCV CSV.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default="reports/forward/shadow_signals.csv")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    df = load_ohlcv_csv(args.data)
    signals = run_signal_engine(df, args.strategy, cfg)
    cols = [c for c in signals.columns if c.startswith("EXP_")]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    signals[cols].reset_index().to_csv(args.out, index=False)
    print(f"saved {len(signals)} shadow rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
