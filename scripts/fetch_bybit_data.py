#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.data.bybit_ohlcv_loader import BybitOHLCVLoader, BybitOHLCVRequest
from src.data.csv_loader import save_ohlcv_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", default="5m")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    loader = BybitOHLCVLoader()
    df = loader.fetch(BybitOHLCVRequest(symbol=args.symbol, timeframe=args.timeframe, limit=args.limit))
    save_ohlcv_csv(df, args.out)
    print(f"saved {len(df)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
