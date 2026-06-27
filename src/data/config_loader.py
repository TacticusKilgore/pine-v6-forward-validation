"""
Configuration loader utilities.

This module provides helper functions to read YAML configuration files and to merge
multiple configuration dictionaries. YAML files are used to parameterize strategies,
symbol universes and default values. The loader ensures that required files exist
and contain valid YAML mappings; empty or missing files raise explicit errors.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required to load YAML configuration files. "
        "Install it via 'pip install PyYAML'."
    ) from exc


def load_yaml_config(path: str | Path) -> Dict[str, Any]:
    """Load a YAML configuration file and return its contents as a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        A dictionary representation of the YAML contents.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or contains invalid YAML.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}") from e

    # A completely empty YAML file results in `None`
    if data is None or (isinstance(data, dict) and not data):
        raise ValueError(f"Configuration file {file_path} is empty or has no mappings")

    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {file_path} must contain a YAML mapping at the top level")

    return data


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two configuration dictionaries.

    Values from ``override`` take precedence over those from ``base``. Nested
    dictionaries are merged recursively. This function does not mutate the inputs;
    instead, it returns a new dictionary containing the merged result.

    Args:
        base: The base configuration dictionary.
        override: The override configuration dictionary.

    Returns:
        A new dictionary representing the merged configuration.
    """
    result: Dict[str, Any] = {}
    # Make sure we don't modify the original base
    for key, value in base.items():
        if isinstance(value, dict):
            result[key] = value.copy()
        else:
            result[key] = value

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = merge_configs(result[key], value)
        else:
            # Override the value completely
            result[key] = value
    return result
