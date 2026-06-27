from __future__ import annotations

from typing import Any
import pandas as pd


def compare_series(a: pd.Series, b: pd.Series, tol: float = 1e-6) -> dict[str, Any]:
    if len(a) != len(b):
        raise ValueError("Series must be of same length to compare")
    mismatches = 0
    max_error = 0.0
    for x, y in zip(a, b):
        if pd.isna(x) and pd.isna(y):
            continue
        if pd.isna(x) or pd.isna(y):
            mismatches += 1
            continue
        err = abs(float(x) - float(y))
        max_error = max(max_error, err)
        if err > tol:
            mismatches += 1
    return {"mismatches": mismatches, "max_error": max_error, "total": len(a)}


def compare_signals(a: pd.Series, b: pd.Series) -> dict[str, int]:
    if len(a) != len(b):
        raise ValueError("Series must be of same length to compare signals")
    mismatches = sum(0 if ((pd.isna(x) and pd.isna(y)) or (not pd.isna(x) and not pd.isna(y) and int(x) == int(y))) else 1 for x, y in zip(a, b))
    return {"mismatches": int(mismatches), "total": len(a)}


def compare_states(a: pd.Series, b: pd.Series) -> dict[str, int]:
    if len(a) != len(b):
        raise ValueError("Series must be of same length to compare states")
    mismatches = sum(0 if ((pd.isna(x) and pd.isna(y)) or x == y) else 1 for x, y in zip(a, b))
    return {"mismatches": int(mismatches), "total": len(a)}


def parity_check(df_pine: pd.DataFrame, df_python: pd.DataFrame, columns: list[str], tol: float = 1e-6) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for col in columns:
        if col not in df_pine.columns or col not in df_python.columns:
            report[col] = {"error": "missing column"}
            continue
        if pd.api.types.is_numeric_dtype(df_pine[col]):
            report[col] = compare_series(df_pine[col], df_python[col], tol)
        else:
            report[col] = compare_states(df_pine[col], df_python[col])
    return report
