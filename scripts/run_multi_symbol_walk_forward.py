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
from src.engine.multi_symbol import evaluate_multi_symbol, write_multi_symbol_report
from src.engine.signal_engine import run_signal_engine


def _parse_symbol_data(values: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("symbol data entries must use SYMBOL=path.csv")
        symbol, path = value.split("=", 1)
        out[symbol.strip()] = path.strip()
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default="amlrx")
    parser.add_argument("--config", default="configs/amlrx_v0_1.yaml")
    parser.add_argument("--symbol-data", nargs="+", required=True)
    parser.add_argument("--out", default="reports/walk_forward/multi_symbol_report.json")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    paths = _parse_symbol_data(args.symbol_data)
    data = {symbol: load_ohlcv_csv(path) for symbol, path in paths.items()}
    report = evaluate_multi_symbol(
        data,
        args.strategy,
        lambda frame: run_signal_engine(frame, args.strategy, cfg),
    )
    write_multi_symbol_report(report, args.out)
    print(
        f"passed={report.passed} symbols={report.symbol_count} "
        f"positive_or_neutral={report.positive_or_neutral_symbols} "
        f"top_symbol_profit_share={report.top_symbol_profit_share:.4f}"
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
