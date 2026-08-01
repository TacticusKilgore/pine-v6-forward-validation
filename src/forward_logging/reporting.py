from __future__ import annotations

from typing import Any

import pandas as pd


def build_forward_summary(signals_with_outcomes: pd.DataFrame) -> dict[str, Any]:
    df = signals_with_outcomes.copy()
    summary: dict[str, Any] = {
        "rows": int(len(df)),
        "by_direction": {},
        "by_regime": {},
    }
    for direction, group in df.groupby("direction", dropna=False):
        summary["by_direction"][str(direction)] = {
            "signals": int(len(group)),
            "mean_return_5_bars": (
                float(group["return_5_bars"].mean())
                if "return_5_bars" in group
                else None
            ),
            "median_mfe_r": float(group["mfe_r"].median()) if "mfe_r" in group else None,
            "median_mae_r": float(group["mae_r"].median()) if "mae_r" in group else None,
        }
    if "regime" in df:
        for regime, group in df.groupby("regime", dropna=False):
            summary["by_regime"][str(regime)] = {"signals": int(len(group))}
    return summary
