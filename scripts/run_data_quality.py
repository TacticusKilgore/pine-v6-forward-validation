#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data.data_quality_gate import build_data_quality_report, write_data_quality_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--symbol", default="not_available")
    parser.add_argument("--timeframe", default="not_available")
    parser.add_argument("--out", default="reports/data_quality/data_quality_report.json")
    args = parser.parse_args()
    report = build_data_quality_report(pd.read_csv(args.data), args.symbol, args.timeframe)
    write_data_quality_report(report, args.out)
    print(f"passed={report.passed} rows={report.rows} missing_candles={report.missing_candles}")
    if report.passed:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
