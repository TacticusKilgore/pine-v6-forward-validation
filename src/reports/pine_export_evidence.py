from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json

import pandas as pd

REQUIRED_EXPORT_COLUMNS = ("timestamp", "EXP_longSignal", "EXP_shortSignal")
RECOMMENDED_EXPORT_COLUMNS = ("EXP_state", "EXP_score")


@dataclass(frozen=True)
class PineExportEvidenceRow:
    strategy: str
    symbol: str
    timeframe: str
    path: str
    exists: bool
    readable: bool
    rows: int
    missing_required_columns: list[str]
    missing_recommended_columns: list[str]
    severity: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PineExportEvidenceReport:
    passed: bool
    rows: list[PineExportEvidenceRow]
    required_columns: tuple[str, ...] = REQUIRED_EXPORT_COLUMNS
    recommended_columns: tuple[str, ...] = RECOMMENDED_EXPORT_COLUMNS

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "required_columns": list(self.required_columns),
            "recommended_columns": list(self.recommended_columns),
            "exports": [row.to_dict() for row in self.rows],
            "summary": summarize_pine_export_evidence(self),
        }


def build_pine_export_evidence_report(
    manifest: dict[str, Any],
    *,
    root: str | Path = ".",
    require_existing_files: bool = False,
) -> PineExportEvidenceReport:
    root_path = Path(root)
    rows: list[PineExportEvidenceRow] = []
    pine_exports = manifest.get("pine_exports", {})
    if not isinstance(pine_exports, dict):
        return PineExportEvidenceReport(
            passed=False,
            rows=[
                PineExportEvidenceRow(
                    strategy="<manifest>",
                    symbol="<manifest>",
                    timeframe="<manifest>",
                    path="pine_exports",
                    exists=False,
                    readable=False,
                    rows=0,
                    missing_required_columns=list(REQUIRED_EXPORT_COLUMNS),
                    missing_recommended_columns=list(RECOMMENDED_EXPORT_COLUMNS),
                    severity="ERROR",
                    message="pine_exports must be a mapping",
                )
            ],
        )

    for strategy, strategy_block in pine_exports.items():
        if not isinstance(strategy_block, dict):
            rows.append(_bad_row(str(strategy), "<unknown>", "<unknown>", f"pine_exports.{strategy}", "strategy export block must be a mapping"))
            continue
        for symbol, symbol_block in strategy_block.items():
            if not isinstance(symbol_block, dict):
                rows.append(_bad_row(str(strategy), str(symbol), "<unknown>", f"pine_exports.{strategy}.{symbol}", "symbol export block must be a mapping"))
                continue
            for timeframe, export_paths in symbol_block.items():
                if not isinstance(export_paths, list) or not export_paths:
                    rows.append(_bad_row(str(strategy), str(symbol), str(timeframe), f"pine_exports.{strategy}.{symbol}.{timeframe}", "export list is empty"))
                    continue
                for export_path in export_paths:
                    rows.append(_evaluate_export_path(str(strategy), str(symbol), str(timeframe), str(export_path), root_path, require_existing_files))

    passed = all(row.severity != "ERROR" for row in rows)
    return PineExportEvidenceReport(passed=passed, rows=rows)


def summarize_pine_export_evidence(report: PineExportEvidenceReport) -> dict[str, Any]:
    total = len(report.rows)
    errors = sum(1 for row in report.rows if row.severity == "ERROR")
    warnings = sum(1 for row in report.rows if row.severity == "WARNING")
    declared = sum(1 for row in report.rows if row.severity == "DECLARED")
    ok = sum(1 for row in report.rows if row.severity == "OK")
    strategies = sorted({row.strategy for row in report.rows})
    symbols = sorted({row.symbol for row in report.rows})
    timeframes = sorted({row.timeframe for row in report.rows})
    return {
        "total_exports": total,
        "ok": ok,
        "declared_only": declared,
        "warnings": warnings,
        "errors": errors,
        "strategies": strategies,
        "symbols": symbols,
        "timeframes": timeframes,
    }


def write_pine_export_evidence_json(report: PineExportEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return out


def write_pine_export_evidence_markdown(report: PineExportEvidenceReport, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = summarize_pine_export_evidence(report)
    lines = [
        "# Pine Export Evidence Report",
        "",
        f"Passed: `{report.passed}`",
        "",
        "## Summary",
        "",
        f"- Total exports: {summary['total_exports']}",
        f"- OK: {summary['ok']}",
        f"- Declared only: {summary['declared_only']}",
        f"- Warnings: {summary['warnings']}",
        f"- Errors: {summary['errors']}",
        "",
        "## Exports",
        "",
        "| Strategy | Symbol | TF | Severity | Rows | Path |",
        "|---|---|---|---|---:|---|",
    ]
    for row in report.rows:
        lines.append(f"| {row.strategy} | {row.symbol} | {row.timeframe} | {row.severity} | {row.rows} | `{row.path}` |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _evaluate_export_path(
    strategy: str,
    symbol: str,
    timeframe: str,
    export_path: str,
    root: Path,
    require_existing_files: bool,
) -> PineExportEvidenceRow:
    full_path = root / export_path
    exists = full_path.is_file()
    if not exists:
        severity = "ERROR" if require_existing_files else "DECLARED"
        return PineExportEvidenceRow(
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            path=export_path,
            exists=False,
            readable=False,
            rows=0,
            missing_required_columns=[] if not require_existing_files else list(REQUIRED_EXPORT_COLUMNS),
            missing_recommended_columns=[],
            severity=severity,
            message="declared but file not checked" if not require_existing_files else "file not found",
        )
    try:
        df = pd.read_csv(full_path)
    except Exception as exc:
        return PineExportEvidenceRow(strategy, symbol, timeframe, export_path, True, False, 0, list(REQUIRED_EXPORT_COLUMNS), list(RECOMMENDED_EXPORT_COLUMNS), "ERROR", f"read failed: {exc}")
    missing_required = [col for col in REQUIRED_EXPORT_COLUMNS if col not in df.columns]
    missing_recommended = [col for col in RECOMMENDED_EXPORT_COLUMNS if col not in df.columns]
    if missing_required:
        severity = "ERROR"
        message = "missing required columns"
    elif missing_recommended:
        severity = "WARNING"
        message = "missing recommended diagnostic columns"
    else:
        severity = "OK"
        message = "export schema accepted"
    return PineExportEvidenceRow(strategy, symbol, timeframe, export_path, True, True, int(len(df)), missing_required, missing_recommended, severity, message)


def _bad_row(strategy: str, symbol: str, timeframe: str, path: str, message: str) -> PineExportEvidenceRow:
    return PineExportEvidenceRow(strategy, symbol, timeframe, path, False, False, 0, list(REQUIRED_EXPORT_COLUMNS), list(RECOMMENDED_EXPORT_COLUMNS), "ERROR", message)
