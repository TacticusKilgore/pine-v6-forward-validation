#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd

from src.data.csv_loader import save_ohlcv_csv


def make_sample_ohlcv(rows: int = 3000, freq: str = "5min", seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=rows, freq=freq, tz="UTC")
    drift = np.linspace(0, 18, rows)
    cycle = np.sin(np.arange(rows) / 38.0) * 7.5 + np.sin(np.arange(rows) / 111.0) * 13.0
    noise = rng.normal(0, 0.65, rows).cumsum() * 0.25
    close = 1000.0 + drift + cycle + noise
    open_ = np.r_[close[0], close[:-1]] + rng.normal(0, 0.25, rows)
    spread = rng.uniform(0.4, 2.2, rows)
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    volume = rng.lognormal(mean=8.1, sigma=0.35, size=rows)
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=idx,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create deterministic sample OHLCV data for local harness smoke tests.")
    parser.add_argument("--out", default="data/processed/sample_BTCUSDT_5m.csv")
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--freq", default="5min")
    args = parser.parse_args()
    df = make_sample_ohlcv(rows=args.rows, freq=args.freq)
    save_ohlcv_csv(df, args.out)
    print(f"wrote={Path(args.out)} rows={len(df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
