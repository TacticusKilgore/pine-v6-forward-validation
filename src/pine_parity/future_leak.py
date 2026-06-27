from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PrefixStabilityMismatch:
    cutoff: int
    timestamp: pd.Timestamp
    column: str
    full_value: object
    prefix_value: object


@dataclass(frozen=True)
class PrefixStabilityReport:
    passed: bool
    checked_cutoffs: int
    mismatches: list[PrefixStabilityMismatch]


def assert_prefix_stability(
    run_fn: Callable[[pd.DataFrame], pd.DataFrame],
    df: pd.DataFrame,
    columns: Iterable[str],
    *,
    warmup_bars: int = 0,
    sample_points: Iterable[int] | None = None,
    rtol: float = 1e-10,
    atol: float = 1e-10,
) -> PrefixStabilityReport:
    """Check whether outputs for completed prefix bars change after future bars are appended.

    A Pine-parity strategy must produce the same value for bar N regardless of whether bars
    N+1...end are present. This detects common Python mistakes such as `shift(-1)`, centered
    windows or future-derived labels leaking into signal columns.
    """
    if len(df) == 0:
        return PrefixStabilityReport(passed=True, checked_cutoffs=0, mismatches=[])
    cols = list(columns)
    if not cols:
        raise ValueError("at least one column must be checked")

    full = run_fn(df).copy()
    if sample_points is None:
        default_points = {warmup_bars + 1, len(df) // 3, len(df) // 2, (len(df) * 2) // 3, len(df) - 1}
        sample_points = sorted(p for p in default_points if warmup_bars < p <= len(df))

    mismatches: list[PrefixStabilityMismatch] = []
    checked = 0
    for cutoff in sample_points:
        cutoff = int(cutoff)
        if cutoff <= warmup_bars or cutoff > len(df):
            continue
        checked += 1
        prefix_df = df.iloc[:cutoff].copy()
        prefix = run_fn(prefix_df).copy()
        compare_index = prefix.index.intersection(full.index)
        if warmup_bars:
            compare_index = compare_index[warmup_bars:]
        for col in cols:
            if col not in full.columns or col not in prefix.columns:
                mismatches.append(
                    PrefixStabilityMismatch(
                        cutoff=cutoff,
                        timestamp=prefix.index[-1],
                        column=col,
                        full_value="<missing>" if col not in full.columns else "<present>",
                        prefix_value="<missing>" if col not in prefix.columns else "<present>",
                    )
                )
                continue
            for ts in compare_index:
                a = full.at[ts, col]
                b = prefix.at[ts, col]
                if _equal(a, b, rtol=rtol, atol=atol):
                    continue
                mismatches.append(
                    PrefixStabilityMismatch(
                        cutoff=cutoff,
                        timestamp=ts,
                        column=col,
                        full_value=a,
                        prefix_value=b,
                    )
                )
                break
    return PrefixStabilityReport(passed=not mismatches, checked_cutoffs=checked, mismatches=mismatches)


def _equal(a: object, b: object, *, rtol: float, atol: float) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    if _is_number(a) and _is_number(b):
        return bool(np.isclose(float(a), float(b), rtol=rtol, atol=atol, equal_nan=True))
    return str(a) == str(b)


def _is_number(value: object) -> bool:
    try:
        float(value)  # type: ignore[arg-type]
        return True
    except (TypeError, ValueError):
        return False
