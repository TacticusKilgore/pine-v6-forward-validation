#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.real_input_manifest import load_real_input_manifest
from src.reports.pine_export_evidence import (
    build_pine_export_evidence_report,
    write_pine_export_evidence_json,
    write_pine_export_evidence_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Pine diagnostic export evidence report")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-existing-files", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()

    manifest = load_real_input_manifest(args.manifest)
    report = build_pine_export_evidence_report(
        manifest,
        root=args.root,
        require_existing_files=args.require_existing_files,
    )
    if args.json_out:
        write_pine_export_evidence_json(report, args.json_out)
    if args.md_out:
        write_pine_export_evidence_markdown(report, args.md_out)
    summary = report.to_dict()["summary"]
    print(
        "passed={passed} total={total} ok={ok} declared={declared} warnings={warnings} errors={errors}".format(
            passed=report.passed,
            total=summary["total_exports"],
            ok=summary["ok"],
            declared=summary["declared_only"],
            warnings=summary["warnings"],
            errors=summary["errors"],
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
