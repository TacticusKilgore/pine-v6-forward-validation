from __future__ import annotations

from pathlib import Path

from src.pine_parity.parity_checker import ParityResult


def write_parity_report(result: ParityResult, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"passed: {result.passed}",
        f"checked_rows: {result.checked_rows}",
        f"mismatch_count: {len(result.mismatches)}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    if not result.mismatches.empty:
        result.mismatches.to_csv(path.with_suffix(".mismatches.csv"), index=False)
