from __future__ import annotations

from typing import Any
import pandas as pd


def ivsf(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    out["ivsf_state"] = "neutral"
    out["signal"] = 0
    out["score"] = 0.0
    out["long_signal"] = 0
    out["short_signal"] = 0
    return out
