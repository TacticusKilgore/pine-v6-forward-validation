"""
Signal engine for strategy modules.

This module provides a central entry point to run different strategies on OHLCV
data. Each strategy returns a DataFrame with at least a ``signal`` column
containing -1 for short, 1 for long and 0 for no action, and a ``score``
column that reflects the confidence or strength of the signal. Strategies may
also add additional diagnostic columns as needed.
"""

from __future__ import annotations

from typing import Dict, Any, Callable

import pandas as pd

from src.strategies.amlrx import amlrx as amlrx_strategy
from src.strategies.iax import iax as iax_strategy
from src.strategies.ivsf import ivsf as ivsf_strategy
try:
    # ELC may not exist if not implemented yet. Import gracefully.
    from src.strategies.elc import elc as elc_strategy
except Exception:  # pragma: no cover - defensive import
    elc_strategy = None  # type: ignore

# Type alias for strategy function
StrategyFunc = Callable[[pd.DataFrame, Dict[str, Any]], pd.DataFrame]


# ---------------------------------------------------------------------------
# Legacy fallback strategy implementations
#
# Historically, the signal engine contained naive placeholder implementations
# of the different strategies directly in this module. These functions are
# preserved for backwards compatibility and can be referenced when the
# dedicated strategy modules are unavailable. The new default behaviour is
# to call the implementations defined in src/strategies/*.py.


def _legacy_strategy_amlrx(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Legacy simplistic AMLR‑X implementation.

    Generates long signals when ``close > open`` and short signals when
    ``close < open``. The score is the relative difference between close
    and open. Config is unused.
    """
    result = df.copy()
    result["score"] = (result["close"] - result["open"]) / result["open"]
    result["signal"] = 0
    result.loc[result["score"] > 0, "signal"] = 1
    result.loc[result["score"] < 0, "signal"] = -1
    return result


def _legacy_strategy_iax(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Legacy simplified IAX implementation.

    Produces signals based on whether the candle closes above or below its
    midpoint. The score reflects the candle body relative to its range.
    """
    result = df.copy()
    body = result["close"] - result["open"]
    rng = result["high"] - result["low"]
    rng = rng.replace(0, pd.NA)
    result["score"] = (body / rng).fillna(0)
    result["signal"] = 0
    result.loc[body > 0, "signal"] = 1
    result.loc[body < 0, "signal"] = -1
    return result


def _legacy_strategy_ivsf(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Legacy placeholder IVSF implementation.

    Returns no signals and zero scores.
    """
    result = df.copy()
    result["score"] = 0.0
    result["signal"] = 0
    return result


def _legacy_strategy_elc(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Legacy simplistic ELC implementation.

    Uses a volatility breakout relative to the previous close. Threshold
    defaults to 0.5%.
    """
    result = df.copy()
    try:
        thresh = float(config.get("threshold", 0.005))
    except Exception:
        thresh = 0.005
    prev_close = result["close"].shift(1)
    result["score"] = 0.0
    result["signal"] = 0
    breakout_long = (result["high"] - prev_close) / prev_close > thresh
    breakout_short = (prev_close - result["low"]) / prev_close > thresh
    result.loc[breakout_long, "signal"] = 1
    result.loc[breakout_short, "signal"] = -1
    score = pd.Series(0.0, index=result.index)
    score.loc[breakout_long] = ((result["high"] - prev_close) / prev_close).loc[breakout_long]
    score.loc[breakout_short] = ((prev_close - result["low"]) / prev_close).loc[breakout_short]
    result["score"] = score.fillna(0.0)
    return result


def run_strategy(df: pd.DataFrame, strategy_name: str, config: Dict[str, Any]) -> pd.DataFrame:
    """Dispatch to the appropriate strategy function.

    Args:
        df: Input OHLCV DataFrame.
        strategy_name: Name of the strategy (amlrx, iax, ivsf, elc).
        config: Strategy‑specific configuration dictionary.

    Returns:
        A DataFrame with at least 'signal' and 'score' columns.

    Raises:
        ValueError: If an unknown strategy is requested.
    """
    name = strategy_name.lower()
    # Dispatch table to dedicated strategy implementations if available.
    dispatch: Dict[str, StrategyFunc] = {}
    dispatch["amlrx"] = amlrx_strategy if callable(amlrx_strategy) else _legacy_strategy_amlrx
    dispatch["iax"] = iax_strategy if callable(iax_strategy) else _legacy_strategy_iax
    dispatch["ivsf"] = ivsf_strategy if callable(ivsf_strategy) else _legacy_strategy_ivsf
    # ELC may not be implemented; fall back to legacy
    if callable(elc_strategy):
        dispatch["elc"] = elc_strategy  # type: ignore
    else:
        dispatch["elc"] = _legacy_strategy_elc
    if name not in dispatch:
        raise ValueError(
            f"Unknown strategy '{strategy_name}'. Known strategies: {', '.join(sorted(dispatch.keys()))}"
        )
    return dispatch[name](df, config)
