#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.pine_parity.export_contract import validate_export_contract, write_export_contract_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default="reports/parity/export_schema_report.json")
    args = parser.parse_args()
    report = validate_export_contract(pd.read_csv(args.csv))
    write_export_contract_report(report, args.out)
    print(f"passed={report.passed} rows={report.rows}")
    if report.passed:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
