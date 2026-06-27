from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd


def write_json_report(payload: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if np.isnan(f) else f
    if isinstance(value, float):
        return None if np.isnan(value) else value
    if hasattr(value, "__dict__"):
        return _json_safe(value.__dict__)
    return value
