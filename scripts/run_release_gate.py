#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reports.release_decision import decide_release, default_framework_gates, write_release_json, write_release_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", default="reports/release/release_decision.json")
    parser.add_argument("--md-out", default="reports/release/release_decision.md")
    args = parser.parse_args()
    decision = decide_release(default_framework_gates())
    write_release_json(decision, args.json_out)
    write_release_markdown(decision, args.md_out)
    print(f"decision={decision.decision} passed_critical={decision.passed_critical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
