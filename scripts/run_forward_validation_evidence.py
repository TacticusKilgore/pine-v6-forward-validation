#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reports.forward_validation_evidence import (
    build_forward_validation_evidence_report,
    load_forward_input,
    write_forward_validation_evidence_json,
    write_forward_validation_evidence_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build causal forward-validation follow-through evidence")
    parser.add_argument("--input", required=True, help="CSV with OHLCV and EXP_longSignal/EXP_shortSignal columns")
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--horizons", nargs="+", type=int, default=[3, 5, 10])
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()

    df = load_forward_input(args.input)
    report = build_forward_validation_evidence_report(
        df,
        strategy=args.strategy,
        symbol=args.symbol,
        timeframe=args.timeframe,
        horizons=args.horizons,
    )
    if args.json_out:
        write_forward_validation_evidence_json(report, args.json_out)
    if args.md_out:
        write_forward_validation_evidence_markdown(report, args.md_out)
    print(
        "passed={passed} rows={rows} signals={signals} horizons={horizons}".format(
            passed=report.passed,
            rows=report.checked_rows,
            signals=report.signal_count,
            horizons=",".join(str(h) for h in report.horizons),
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
