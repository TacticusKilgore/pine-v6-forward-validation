from __future__ import annotations

from pathlib import Path
import pytest

from src.data.config_loader import load_yaml_config, merge_configs


def test_load_yaml_config_reads_file(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    p.write_text("key: value\nnumber: 42\n", encoding="utf-8")
    assert load_yaml_config(p) == {"key": "value", "number": 42}


def test_load_yaml_config_empty_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "empty.yaml"
    p.touch()
    with pytest.raises(ValueError):
        load_yaml_config(p)


def test_load_yaml_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_yaml_config(tmp_path / "missing.yaml")


def test_merge_configs_deep_merge() -> None:
    assert merge_configs({"a":1,"b":{"x":2,"y":3}}, {"b":{"y":30,"z":40}}) == {"a":1,"b":{"x":2,"y":30,"z":40}}
