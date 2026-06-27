from __future__ import annotations

from pathlib import Path


def write_summary_report(summary: dict, out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(["# Summary Report", "", *[f"- **{k}**: {v}" for k, v in summary.items()]]) + "\n", encoding="utf-8")
    return path
