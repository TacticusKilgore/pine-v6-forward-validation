#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reports.parity_evidence import (
    build_parity_evidence_report,
    write_parity_evidence_json,
    write_parity_evidence_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real Pine-vs-Python parity evidence report")
    parser.add_argument("--pine-export", required=True)
    parser.add_argument("--python-output", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()

    report = build_parity_evidence_report(
        pine_export_path=args.pine_export,
        python_output_path=args.python_output,
        strategy=args.strategy,
        symbol=args.symbol,
        timeframe=args.timeframe,
        root=args.root,
    )
    if args.json_out:
        write_parity_evidence_json(report, args.json_out)
    if args.md_out:
        write_parity_evidence_markdown(report, args.md_out)
    print(
        "passed={passed} severity={severity} rows={rows} mismatches={mismatches} critical={critical} signal_rate={signal_rate} direction_rate={direction_rate}".format(
            passed=report.passed,
            severity=report.severity,
            rows=report.checked_rows,
            mismatches=report.mismatch_count,
            critical=report.critical_mismatches,
            signal_rate=report.signal_bar_match_rate,
            direction_rate=report.direction_match_rate,
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
