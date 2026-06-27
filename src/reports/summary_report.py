from __future__ import annotations

from pathlib import Path
from typing import Any


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.2f}%"


def write_summary_report(summary: dict[str, Any] | list[dict[str, Any]], out: str | Path) -> Path:
    rows = [summary] if isinstance(summary, dict) else list(summary)
    if not rows:
        raise ValueError("Summary report cannot be written because summary is empty")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Forward Return Summary", "", "| Horizon (bars) | Signals | Long | Short | Mean Return | Median Return | Win Rate |", "|---:|---:|---:|---:|---:|---:|---:|"]
    for item in rows:
        lines.append(
            "| {h} | {n} | {l} | {s} | {m} | {md} | {w} |".format(
                h=item.get("horizon"),
                n=item.get("signals_total"),
                l=item.get("long_signals"),
                s=item.get("short_signals"),
                m=_pct(item.get("mean_forward_return")),
                md=_pct(item.get("median_forward_return")),
                w=_pct(item.get("win_rate")),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
