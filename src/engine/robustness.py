"""
Robustness and negative control evaluations.

This module provides utilities to assess the stability of a trading strategy
under various perturbations. Robustness testing helps determine whether
performance is due to genuine signal edge rather than noise, overfitting or
favourable market conditions. The functions herein implement different
perturbations including parameter variation, cost sensitivity and signal
scrambling. Each function returns either a modified configuration, a modified
DataFrame of signals or computed metrics that can be compared against
baseline results.

The overall robustness score is a simple composite: the average difference
between the baseline mean return and the mean return under each perturbation.
Lower values indicate more robust strategies. A strategy that performs
similarly under perturbations (low degradation) is considered more robust.
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd


def parameter_perturbation(base_config: Dict[str, Any], perturbations: Dict[str, float]) -> List[Dict[str, Any]]:
    """Generate perturbed configurations around a base configuration.

    Each numeric parameter in ``perturbations`` specifies the relative
    perturbation applied to the corresponding key in ``base_config``. For
    example, ``perturbations = {"atr_length": 0.2}`` will create two
    configurations where ``atr_length`` is decreased and increased by 20%.

    Args:
        base_config: Original configuration dictionary.
        perturbations: Mapping of parameter names to relative perturbations.

    Returns:
        List of new configuration dictionaries including the original config.
    """
    configs = [base_config.copy()]
    for key, rel in perturbations.items():
        if key not in base_config:
            continue
        try:
            base_val = float(base_config[key])
        except Exception:
            continue
        # Decrease and increase
        configs.append({**base_config, key: base_val * (1 - rel)})
        configs.append({**base_config, key: base_val * (1 + rel)})
    return configs


def cost_sensitivity(cost_params: Dict[str, float], variations: List[float]) -> List[Dict[str, float]]:
    """Generate cost parameter variations for sensitivity analysis.

    For each variation factor in ``variations``, a new cost parameter set
    is created where all cost components are scaled by that factor.

    Args:
        cost_params: Baseline cost parameters (maker_fee_bps, taker_fee_bps,
            slippage_bps).
        variations: List of multiplicative factors (e.g. 0.5, 1.5).

    Returns:
        List of cost parameter dictionaries including the baseline.
    """
    param_sets = [cost_params.copy()]
    for factor in variations:
        varied = {
            k: float(v) * factor for k, v in cost_params.items()
        }
        param_sets.append(varied)
    return param_sets


def random_signal_control(df: pd.DataFrame, seed: int | None = None) -> pd.DataFrame:
    """Generate a control DataFrame with randomised signals.

    The ``signal`` column of the input DataFrame is replaced with random
    long/short/no‑action signals drawn from the empirical distribution of
    signal counts. Scores are set to zero. This simulates a strategy with no
    predictive power.

    Args:
        df: DataFrame with a ``signal`` column.
        seed: Optional random seed for reproducibility.

    Returns:
        A copy of ``df`` with randomised signals and zero scores.
    """
    rng = np.random.default_rng(seed)
    counts = df["signal"].value_counts().to_dict()
    # Build probability distribution across -1, 0, 1
    total = sum(counts.get(x, 0) for x in (-1, 0, 1))
    probs = [counts.get(-1, 0) / total, counts.get(0, 0) / total, counts.get(1, 0) / total]
    choices = rng.choice([-1, 0, 1], size=len(df), p=probs)
    result = df.copy()
    result["signal"] = choices
    result["score"] = 0.0
    return result


def shifted_signal_control(df: pd.DataFrame, shift: int) -> pd.DataFrame:
    """Shift signals by a specified number of bars to create a control.

    A positive shift moves signals into the future (lookahead), while a
    negative shift delays signals. This tests whether temporal alignment of
    signals matters. Scores are set to zero.

    Args:
        df: DataFrame with a ``signal`` column.
        shift: Number of rows to shift the signal series.

    Returns:
        A copy of ``df`` with shifted signals and zero scores.
    """
    result = df.copy()
    result["signal"] = result["signal"].shift(shift).fillna(0).astype(int)
    result["score"] = 0.0
    return result


def inverted_signal_control(df: pd.DataFrame) -> pd.DataFrame:
    """Invert signals to create a contrarian control.

    All long signals become short and vice versa. Neutral signals remain.
    Scores are negated to reflect the inverted conviction.

    Args:
        df: DataFrame with a ``signal`` column.

    Returns:
        A copy of ``df`` with inverted signals and negated scores.
    """
    result = df.copy()
    result["signal"] = result["signal"] * -1
    result["score"] = result.get("score", 0) * -1
    return result


def shuffled_return_control(df: pd.DataFrame, horizon_col: str, seed: int | None = None) -> pd.DataFrame:
    """Shuffle forward returns to break the link between signal timing and outcomes.

    Args:
        df: DataFrame containing a forward return column (e.g. ``fwd_return_5``).
        horizon_col: Name of the forward return column to shuffle.
        seed: Optional random seed for reproducibility.

    Returns:
        A copy of ``df`` with the specified forward returns shuffled.
    """
    result = df.copy()
    rng = np.random.default_rng(seed)
    shuffled = result[horizon_col].dropna().sample(frac=1.0, random_state=seed).reset_index(drop=True)
    result.loc[result[horizon_col].notna(), horizon_col] = shuffled.values
    return result


def robustness_score(baseline_returns: List[float], perturbed_returns: List[List[float]]) -> float:
    """Compute a simple robustness score.

    The score is the average absolute difference between the mean baseline
    return and the mean return of each perturbation. Lower scores indicate
    more robust strategies.

    Args:
        baseline_returns: List of forward returns from the baseline strategy.
        perturbed_returns: List of lists of forward returns for each
            perturbation.

    Returns:
        A non‑negative float representing robustness (lower is better).
    """
    if not baseline_returns:
        return float("nan")
    base_mean = float(np.mean(baseline_returns))
    diffs = []
    for returns in perturbed_returns:
        if not returns:
            continue
        diffs.append(abs(base_mean - float(np.mean(returns))))
    return float(np.mean(diffs)) if diffs else float("nan")