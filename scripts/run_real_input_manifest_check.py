#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.real_input_manifest import (
    load_real_input_manifest,
    validate_real_input_manifest,
    write_manifest_validation_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate real Bybit/Pine input manifest coverage")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--json-out")
    parser.add_argument("--require-existing-files", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    manifest = load_real_input_manifest(args.manifest)
    result = validate_real_input_manifest(
        manifest,
        require_existing_files=args.require_existing_files,
        root=args.root,
    )
    if args.json_out:
        write_manifest_validation_json(result, args.json_out)
    print(
        "passed={passed} errors={errors} warnings={warnings}".format(
            passed=result.passed,
            errors=len(result.errors),
            warnings=len(result.warnings),
        )
    )
    for finding in result.errors[:20]:
        print(f"ERROR {finding.code} {finding.path}: {finding.message}")
    for finding in result.warnings[:20]:
        print(f"WARNING {finding.code} {finding.path}: {finding.message}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
