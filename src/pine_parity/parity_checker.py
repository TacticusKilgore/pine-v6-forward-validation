from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class ParityResult:
    column: str
    compared: int
    mismatches: int
    max_abs_error: float
    passed: bool


def compare_series(left: pd.Series, right: pd.Series, column: str, tolerance: float = 1e-8) -> ParityResult:
    aligned = pd.concat([left.rename("left"), right.rename("right")], axis=1).dropna()
    diff = (aligned["left"] - aligned["right"]).abs() if not aligned.empty else pd.Series(dtype=float)
    mismatches = int((diff > tolerance).sum())
    return ParityResult(column, int(len(aligned)), mismatches, float(diff.max()) if len(diff) else 0.0, mismatches == 0)
