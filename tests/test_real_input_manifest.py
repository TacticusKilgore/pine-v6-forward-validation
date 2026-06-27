from __future__ import annotations

from pathlib import Path

import pytest

from src.data.real_input_manifest import (
    load_real_input_manifest,
    validate_real_input_manifest,
    write_manifest_validation_json,
)


def complete_manifest() -> dict:
    return {
        "version": 1,
        "required": {
            "strategies": ["amlrx", "iax"],
            "symbols": ["BTCUSDT", "ETHUSDT"],
            "timeframes": ["5m", "15m"],
        },
        "bybit_ohlcv": {
            "BTCUSDT": {"5m": "data/raw/bybit/BTCUSDT/5m/BTCUSDT_5m.csv", "15m": "data/raw/bybit/BTCUSDT/15m/BTCUSDT_15m.csv"},
            "ETHUSDT": {"5m": "data/raw/bybit/ETHUSDT/5m/ETHUSDT_5m.csv", "15m": "data/raw/bybit/ETHUSDT/15m/ETHUSDT_15m.csv"},
        },
        "pine_exports": {
            "amlrx": {"BTCUSDT": {"5m": ["data/pine_exports/amlrx/BTCUSDT/5m/export.csv"]}},
            "iax": {"BTCUSDT": {"5m": ["data/pine_exports/iax/BTCUSDT/5m/export.csv"]}},
        },
    }


def test_complete_manifest_passes_without_file_existence_check() -> None:
    result = validate_real_input_manifest(complete_manifest(), require_existing_files=False)
    assert result.passed
    assert result.errors == []
    assert result.required_symbols == ["BTCUSDT", "ETHUSDT"]


def test_missing_ohlcv_and_exports_fail() -> None:
    manifest = complete_manifest()
    manifest["bybit_ohlcv"]["ETHUSDT"].pop("15m")
    manifest["pine_exports"].pop("iax")
    result = validate_real_input_manifest(manifest, require_existing_files=False)
    assert not result.passed
    codes = {item.code for item in result.errors}
    assert "missing_ohlcv_path" in codes
    assert "missing_strategy_exports" in codes


def test_file_existence_check_fails_when_paths_absent(tmp_path: Path) -> None:
    result = validate_real_input_manifest(
        complete_manifest(),
        require_existing_files=True,
        root=tmp_path,
    )
    assert not result.passed
    assert any(item.code == "ohlcv_file_not_found" for item in result.errors)
    assert any(item.code == "export_file_not_found" for item in result.errors)


def test_load_manifest_and_write_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(
        "version: 1\nrequired:\n  strategies: [amlrx]\n  symbols: [BTCUSDT]\n  timeframes: [5m]\nbybit_ohlcv:\n  BTCUSDT:\n    5m: data/raw/bybit/BTCUSDT/5m/BTCUSDT_5m.csv\npine_exports:\n  amlrx:\n    BTCUSDT:\n      5m:\n        - data/pine_exports/amlrx/BTCUSDT/5m/export.csv\n",
        encoding="utf-8",
    )
    manifest = load_real_input_manifest(manifest_path)
    result = validate_real_input_manifest(manifest)
    out = write_manifest_validation_json(result, tmp_path / "report.json")
    assert out.is_file()
    assert '"passed": true' in out.read_text(encoding="utf-8")


def test_load_missing_manifest_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_real_input_manifest(tmp_path / "missing.yaml")
