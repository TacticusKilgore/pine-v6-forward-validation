from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json

import yaml


@dataclass(frozen=True)
class ManifestFinding:
    level: str
    code: str
    message: str
    path: str = ""


@dataclass(frozen=True)
class ManifestValidationResult:
    passed: bool
    errors: list[ManifestFinding]
    warnings: list[ManifestFinding]
    required_strategies: list[str]
    required_symbols: list[str]
    required_timeframes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": [asdict(item) for item in self.errors],
            "warnings": [asdict(item) for item in self.warnings],
            "required_strategies": self.required_strategies,
            "required_symbols": self.required_symbols,
            "required_timeframes": self.required_timeframes,
        }


def load_real_input_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if data is None:
        raise ValueError(f"Manifest is empty: {manifest_path}")
    if not isinstance(data, dict):
        raise ValueError("Manifest top-level value must be a mapping")
    return data


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _finding(level: str, code: str, message: str, path: str = "") -> ManifestFinding:
    return ManifestFinding(level=level, code=code, message=message, path=path)


def validate_real_input_manifest(
    manifest: dict[str, Any],
    *,
    require_existing_files: bool = False,
    root: str | Path = ".",
) -> ManifestValidationResult:
    errors: list[ManifestFinding] = []
    warnings: list[ManifestFinding] = []
    required = manifest.get("required", {})
    if not isinstance(required, dict):
        errors.append(_finding("ERROR", "required_not_mapping", "required must be a mapping", "required"))
        required = {}

    strategies = _string_list(required.get("strategies"))
    symbols = _string_list(required.get("symbols"))
    timeframes = _string_list(required.get("timeframes"))

    if not strategies:
        errors.append(_finding("ERROR", "missing_strategies", "required.strategies is empty", "required.strategies"))
    if not symbols:
        errors.append(_finding("ERROR", "missing_symbols", "required.symbols is empty", "required.symbols"))
    if not timeframes:
        errors.append(_finding("ERROR", "missing_timeframes", "required.timeframes is empty", "required.timeframes"))

    bybit_ohlcv = manifest.get("bybit_ohlcv", {})
    if not isinstance(bybit_ohlcv, dict):
        errors.append(_finding("ERROR", "bybit_ohlcv_not_mapping", "bybit_ohlcv must be a mapping", "bybit_ohlcv"))
        bybit_ohlcv = {}

    root_path = Path(root)
    for symbol in symbols:
        symbol_block = bybit_ohlcv.get(symbol)
        if not isinstance(symbol_block, dict):
            errors.append(_finding("ERROR", "missing_symbol_ohlcv", f"Missing OHLCV block for {symbol}", f"bybit_ohlcv.{symbol}"))
            continue
        for timeframe in timeframes:
            value = symbol_block.get(timeframe)
            field = f"bybit_ohlcv.{symbol}.{timeframe}"
            if not isinstance(value, str) or not value:
                errors.append(_finding("ERROR", "missing_ohlcv_path", f"Missing OHLCV path for {symbol} {timeframe}", field))
            elif require_existing_files and not (root_path / value).is_file():
                errors.append(_finding("ERROR", "ohlcv_file_not_found", f"OHLCV file not found: {value}", field))

    pine_exports = manifest.get("pine_exports", {})
    if not isinstance(pine_exports, dict):
        errors.append(_finding("ERROR", "pine_exports_not_mapping", "pine_exports must be a mapping", "pine_exports"))
        pine_exports = {}

    for strategy in strategies:
        strategy_block = pine_exports.get(strategy)
        if not isinstance(strategy_block, dict):
            errors.append(_finding("ERROR", "missing_strategy_exports", f"Missing export block for {strategy}", f"pine_exports.{strategy}"))
            continue
        has_export = False
        for symbol, symbol_block in strategy_block.items():
            if symbol not in symbols:
                warnings.append(_finding("WARNING", "unexpected_symbol", f"Unexpected symbol {symbol}", f"pine_exports.{strategy}.{symbol}"))
            if not isinstance(symbol_block, dict):
                errors.append(_finding("ERROR", "export_symbol_not_mapping", "Symbol export block must be a mapping", f"pine_exports.{strategy}.{symbol}"))
                continue
            for timeframe, paths in symbol_block.items():
                field = f"pine_exports.{strategy}.{symbol}.{timeframe}"
                if timeframe not in timeframes:
                    warnings.append(_finding("WARNING", "unexpected_timeframe", f"Unexpected timeframe {timeframe}", field))
                if not isinstance(paths, list) or not paths:
                    errors.append(_finding("ERROR", "empty_export_list", "Export path list is empty", field))
                    continue
                has_export = True
                for idx, item in enumerate(paths):
                    item_field = f"{field}[{idx}]"
                    if not isinstance(item, str) or not item:
                        errors.append(_finding("ERROR", "bad_export_path", "Export path must be a string", item_field))
                    elif require_existing_files and not (root_path / item).is_file():
                        errors.append(_finding("ERROR", "export_file_not_found", f"Export file not found: {item}", item_field))
        if not has_export:
            errors.append(_finding("ERROR", "strategy_has_no_exports", f"No export paths found for {strategy}", f"pine_exports.{strategy}"))

    return ManifestValidationResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
        required_strategies=strategies,
        required_symbols=symbols,
        required_timeframes=timeframes,
    )


def write_manifest_validation_json(result: ManifestValidationResult, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return out
