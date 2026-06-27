#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.replay.reconciliation import reconcile_signal_frames, write_reconciliation_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pine-export", required=True)
    parser.add_argument("--shadow-output", required=True)
    parser.add_argument("--out", default="reports/forward/reconciliation_report.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = reconcile_signal_frames(pd.read_csv(args.pine_export), pd.read_csv(args.shadow_output))
    write_reconciliation_report(report, args.out)
    print(
        f"passed={report.passed} rows={report.rows} matched={report.matched_rows} "
        f"mismatches={report.signal_mismatches} direction_match_rate={report.direction_match_rate:.4f}"
    )
    if args.strict and not report.passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
