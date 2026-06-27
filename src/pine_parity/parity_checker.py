from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
import numpy as np
import pandas as pd

DEFAULT_REQUIRED_COLUMNS = (
    "EXP_longSignal",
    "EXP_shortSignal",
)


@dataclass(frozen=True)
class ParityConfig:
    score_tolerance: float = 1e-6
    price_tolerance_bps: float = 1.0
    required_columns: tuple[str, ...] = field(default_factory=lambda: DEFAULT_REQUIRED_COLUMNS)
    require_signal_bar_match: bool = True


@dataclass
class ParityResult:
    passed: bool
    checked_rows: int
    mismatches: pd.DataFrame
    missing_columns: list[str]
    common_columns: list[str]


def check_parity(
    pine_export: pd.DataFrame,
    python_output: pd.DataFrame,
    config: ParityConfig | None = None,
) -> ParityResult:
    """Compare Pine diagnostic export against Python output.

    Both inputs must use the same timestamp index or contain a timestamp column.
    Required columns are enforced, while all additional overlapping diagnostic columns are
    compared. Price-like columns use BPS tolerance, score columns use absolute tolerance.
    """
    config = config or ParityConfig()
    pine = _normalize(pine_export)
    py = _normalize(python_output)

    common_index = pine.index.intersection(py.index)
    common_cols = [c for c in pine.columns if c in py.columns]
    missing_columns = _missing_required_columns(config.required_columns, pine, py)
    mismatches: list[dict[str, object]] = []

    if len(common_index) == 0:
        mismatches.append({"timestamp": None, "column": "<index>", "pine": "no overlap", "python": "no overlap"})

    for idx in common_index:
        for col in common_cols:
            a = pine.at[idx, col]
            b = py.at[idx, col]
            if _values_match(a, b, col, config):
                continue
            mismatches.append({"timestamp": idx, "column": col, "pine": a, "python": b})

    if config.require_signal_bar_match:
        for col in ["EXP_longSignal", "EXP_shortSignal"]:
            if col in pine.columns and col in py.columns:
                pine_signal_times = set(pine.index[_as_bool(pine[col]).reindex(pine.index, fill_value=False)])
                py_signal_times = set(py.index[_as_bool(py[col]).reindex(py.index, fill_value=False)])
                for missing_ts in sorted(pine_signal_times - py_signal_times):
                    mismatches.append({"timestamp": missing_ts, "column": col, "pine": True, "python": False})
                for extra_ts in sorted(py_signal_times - pine_signal_times):
                    mismatches.append({"timestamp": extra_ts, "column": col, "pine": False, "python": True})

    for col in missing_columns:
        mismatches.append({"timestamp": None, "column": col, "pine": "required", "python": "missing"})

    mismatch_df = pd.DataFrame(mismatches)
    return ParityResult(
        passed=mismatch_df.empty,
        checked_rows=len(common_index),
        mismatches=mismatch_df,
        missing_columns=missing_columns,
        common_columns=common_cols,
    )


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
        out = out.set_index("timestamp")
    elif isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index, utc=True)
    else:
        raise ValueError("parity inputs must contain timestamp column or use DatetimeIndex")
    return out.sort_index()


def _missing_required_columns(required_columns: Iterable[str], pine: pd.DataFrame, py: pd.DataFrame) -> list[str]:
    missing: list[str] = []
    for col in required_columns:
        if col not in pine.columns or col not in py.columns:
            missing.append(col)
    return missing


def _values_match(a: object, b: object, col: str, config: ParityConfig) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    col_l = col.lower()
    if any(token in col_l for token in ["price", "stop", "tp", "target"]):
        return _numeric_close(a, b, rtol=0.0, atol=abs(float(a)) * config.price_tolerance_bps / 10_000.0)
    if "score" in col_l:
        return _numeric_close(a, b, rtol=0.0, atol=config.score_tolerance)
    if _looks_bool(a) or _looks_bool(b):
        return bool(_to_bool(a)) == bool(_to_bool(b))
    return str(a) == str(b)


def _numeric_close(a: object, b: object, *, rtol: float, atol: float) -> bool:
    try:
        return bool(np.isclose(float(a), float(b), rtol=rtol, atol=atol, equal_nan=True))
    except (TypeError, ValueError):
        return False


def _looks_bool(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return True
    return str(value).strip().lower() in {"true", "false", "1", "0", "yes", "no"}


def _to_bool(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    s = str(value).strip().lower()
    if s in {"true", "1", "yes"}:
        return True
    if s in {"false", "0", "no", "nan", "none"}:
        return False
    return bool(value)


def _as_bool(series: pd.Series) -> pd.Series:
    return series.map(_to_bool).astype(bool)
