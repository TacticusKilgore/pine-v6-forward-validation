from __future__ import annotations

import argparse
from src.data.bybit_ohlcv_loader import fetch_bybit_ohlcv


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--timeframe", default="5m")
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    fetch_bybit_ohlcv(a.symbol, a.timeframe, a.limit, a.out)

if __name__ == "__main__":
    main()
