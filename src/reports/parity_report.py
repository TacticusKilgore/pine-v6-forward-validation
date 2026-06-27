from __future__ import annotations

from pathlib import Path


def write_parity_report(results: list, out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Parity Report\n\n" + repr(results) + "\n", encoding="utf-8")
    return path
