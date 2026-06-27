from __future__ import annotations

import pandas as pd
import pytest

from src.data.pine_export_schema import inspect_pine_export_schema, validate_pine_export


def valid_pine_export_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z", "2026-01-01T00:05:00Z", "2026-01-01T00:10:00Z"],
            "EXP_longSignal": [0, 1, 0],
            "EXP_shortSignal": [0, 0, 1],
            "EXP_state": ["Neutral", "Active Long", "Active Short"],
            "EXP_score": [0.0, 70.0, 65.0],
        }
    )


def test_validate_pine_export_accepts_valid_frame() -> None:
    validate_pine_export(valid_pine_export_df())
    report = inspect_pine_export_schema(valid_pine_export_df())
    assert report.passed
    assert report.rows == 3


def test_validate_pine_export_rejects_missing_required_column() -> None:
    df = valid_pine_export_df().drop(columns=["EXP_shortSignal"])
    with pytest.raises(ValueError):
        validate_pine_export(df)


def test_validate_pine_export_rejects_duplicate_timestamps() -> None:
    df = valid_pine_export_df()
    df.loc[2, "timestamp"] = df.loc[1, "timestamp"]
    with pytest.raises(ValueError):
        validate_pine_export(df)


def test_validate_pine_export_rejects_unsorted_timestamps() -> None:
    df = valid_pine_export_df()
    df.loc[2, "timestamp"] = "2025-12-31T23:55:00Z"
    with pytest.raises(ValueError):
        validate_pine_export(df)


def test_validate_pine_export_rejects_null_signal() -> None:
    df = valid_pine_export_df()
    df.loc[1, "EXP_longSignal"] = None
    with pytest.raises(ValueError):
        validate_pine_export(df)


def test_validate_pine_export_rejects_non_binary_signal() -> None:
    df = valid_pine_export_df()
    df.loc[1, "EXP_longSignal"] = 2
    with pytest.raises(ValueError):
        validate_pine_export(df)


def test_validate_pine_export_warns_missing_recommended_columns() -> None:
    df = valid_pine_export_df().drop(columns=["EXP_state", "EXP_score"])
    report = inspect_pine_export_schema(df)
    assert report.passed
    assert report.missing_recommended_columns == ["EXP_state", "EXP_score"]
