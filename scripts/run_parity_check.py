#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import yaml
import pandas as pd

from src.data.csv_loader import load_ohlcv_csv
from src.engine.signal_engine import run_signal_engine
from src.pine_parity.parity_checker import ParityConfig, check_parity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pine-export", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ohlcv", help="Optional OHLCV CSV. If omitted, pine export must contain OHLCV columns.")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    pine = pd.read_csv(args.pine_export)
    df = load_ohlcv_csv(args.ohlcv) if args.ohlcv else load_ohlcv_csv(args.pine_export)
    py = run_signal_engine(df, args.strategy, cfg)
    result = check_parity(pine, py.reset_index(), ParityConfig())
    print(f"passed={result.passed} checked_rows={result.checked_rows} mismatches={len(result.mismatches)}")
    if not result.mismatches.empty:
        print(result.mismatches.head(20).to_string(index=False))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
