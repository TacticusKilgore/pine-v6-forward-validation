from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

REQUIRED_PINE_EXPORT_COLUMNS = ("timestamp", "EXP_longSignal", "EXP_shortSignal")
RECOMMENDED_PINE_EXPORT_COLUMNS = ("EXP_state", "EXP_score")


@dataclass(frozen=True)
class PineExportSchemaReport:
    passed: bool
    rows: int
    missing_required_columns: list[str]
    missing_recommended_columns: list[str]
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_pine_export_schema(df: pd.DataFrame) -> PineExportSchemaReport:
    errors: list[str] = []
    warnings: list[str] = []
    missing_required = [column for column in REQUIRED_PINE_EXPORT_COLUMNS if column not in df.columns]
    missing_recommended = [column for column in RECOMMENDED_PINE_EXPORT_COLUMNS if column not in df.columns]

    if missing_required:
        errors.append(f"missing required columns: {missing_required}")
        return PineExportSchemaReport(False, int(len(df)), missing_required, missing_recommended, errors, warnings)

    try:
        timestamps = pd.to_datetime(df["timestamp"], utc=True)
    except Exception as exc:
        errors.append(f"timestamp parse failed: {exc}")
        return PineExportSchemaReport(False, int(len(df)), missing_required, missing_recommended, errors, warnings)

    if timestamps.isna().any():
        errors.append("timestamp contains null or unparseable values")
    if timestamps.duplicated().any():
        errors.append("timestamp contains duplicates")
    if not timestamps.is_monotonic_increasing:
        errors.append("timestamp must be sorted ascending")

    for column in ("EXP_longSignal", "EXP_shortSignal"):
        numeric = pd.to_numeric(df[column], errors="coerce")
        if numeric.isna().any():
            errors.append(f"{column} must be numeric/boolean-like")
        invalid_values = set(numeric.dropna().astype(int).unique()) - {0, 1}
        if invalid_values:
            errors.append(f"{column} must only contain 0/1 values; found {sorted(invalid_values)}")

    if missing_recommended:
        warnings.append(f"missing recommended diagnostic columns: {missing_recommended}")
    if len(df) == 0:
        warnings.append("export is empty")

    return PineExportSchemaReport(not errors, int(len(df)), missing_required, missing_recommended, errors, warnings)


def validate_pine_export(df: pd.DataFrame) -> None:
    report = inspect_pine_export_schema(df)
    if not report.passed:
        raise ValueError("Pine export schema validation failed: " + "; ".join(report.errors))
