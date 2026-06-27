from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RobustScoreComponents:
    forward_expectancy: float
    profit_factor: float
    drawdown_control: float
    trade_count_adequacy: float
    win_rate: float
    long_short_balance: float
    total: float


def trade_metrics(trades: pd.DataFrame) -> dict[str, float]:
    if trades.empty:
        return {
            "trade_count": 0.0,
            "expectancy_r": 0.0,
            "profit_factor": 0.0,
            "win_rate": 0.0,
            "avg_r": 0.0,
            "median_r": 0.0,
            "max_drawdown_r": 0.0,
            "gross_r_sum": 0.0,
            "net_r_sum": 0.0,
            "long_trade_count": 0.0,
            "short_trade_count": 0.0,
            "long_expectancy_r": 0.0,
            "short_expectancy_r": 0.0,
        }
    r = trades["net_r"].astype(float)
    wins = r[r > 0]
    losses = r[r < 0]
    equity = r.cumsum()
    dd = equity - equity.cummax()
    long_r = trades.loc[trades.get("side", "") == "long", "net_r"].astype(float) if "side" in trades else pd.Series(dtype=float)
    short_r = trades.loc[trades.get("side", "") == "short", "net_r"].astype(float) if "side" in trades else pd.Series(dtype=float)
    return {
        "trade_count": float(len(r)),
        "expectancy_r": float(r.mean()),
        "profit_factor": _safe_profit_factor(wins.sum(), losses.sum()),
        "win_rate": float((r > 0).mean()),
        "avg_r": float(r.mean()),
        "median_r": float(r.median()),
        "max_drawdown_r": float(abs(dd.min())) if len(dd) else 0.0,
        "gross_r_sum": float(trades["gross_r"].sum()) if "gross_r" in trades else float("nan"),
        "net_r_sum": float(r.sum()),
        "long_trade_count": float(len(long_r)),
        "short_trade_count": float(len(short_r)),
        "long_expectancy_r": float(long_r.mean()) if len(long_r) else 0.0,
        "short_expectancy_r": float(short_r.mean()) if len(short_r) else 0.0,
    }


def side_metrics(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty or "side" not in trades.columns:
        return pd.DataFrame()
    rows = []
    for side, group in trades.groupby("side"):
        row = {"side": side, **trade_metrics(group)}
        rows.append(row)
    return pd.DataFrame(rows)


def robust_score(metrics: dict[str, float]) -> float:
    return robust_score_components(metrics).total


def robust_score_components(metrics: dict[str, float]) -> RobustScoreComponents:
    expectancy_component = (math.tanh(metrics.get("expectancy_r", 0.0)) * 0.5 + 0.5) * 25.0
    pf = metrics.get("profit_factor", 0.0)
    pf_component = 20.0 if math.isinf(pf) and metrics.get("trade_count", 0.0) > 0 else min(max(pf, 0.0), 3.0) / 3.0 * 20.0
    drawdown_component = max(0.0, 15.0 - min(metrics.get("max_drawdown_r", 0.0), 15.0))
    trade_component = min(metrics.get("trade_count", 0.0), 100.0) / 100.0 * 15.0
    win_component = min(max(metrics.get("win_rate", 0.0), 0.0), 1.0) * 10.0
    balance_component = _long_short_balance_component(metrics) * 15.0
    total = expectancy_component + pf_component + drawdown_component + trade_component + win_component + balance_component
    return RobustScoreComponents(
        forward_expectancy=float(expectancy_component),
        profit_factor=float(pf_component),
        drawdown_control=float(drawdown_component),
        trade_count_adequacy=float(trade_component),
        win_rate=float(win_component),
        long_short_balance=float(balance_component),
        total=float(max(0.0, min(100.0, total))),
    )


def _safe_profit_factor(win_sum: float, loss_sum: float) -> float:
    if abs(loss_sum) == 0:
        return float("inf") if win_sum > 0 else 0.0
    return float(win_sum / abs(loss_sum))


def _long_short_balance_component(metrics: dict[str, float]) -> float:
    long_n = metrics.get("long_trade_count", 0.0)
    short_n = metrics.get("short_trade_count", 0.0)
    total = long_n + short_n
    if total == 0:
        return 0.0
    if long_n == 0 or short_n == 0:
        return 0.35
    count_balance = 1.0 - abs(long_n - short_n) / total
    long_exp = metrics.get("long_expectancy_r", 0.0)
    short_exp = metrics.get("short_expectancy_r", 0.0)
    exp_balance = 1.0 if long_exp >= 0 and short_exp >= 0 else 0.5 if max(long_exp, short_exp) >= 0 else 0.0
    return float(max(0.0, min(1.0, 0.6 * count_balance + 0.4 * exp_balance)))
