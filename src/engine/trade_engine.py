from __future__ import annotations

from typing import Any
import pandas as pd


def evaluate_forward_returns(df: pd.DataFrame, horizon_bars: int) -> pd.DataFrame:
    if horizon_bars <= 0:
        raise ValueError("horizon_bars must be positive")
    if "signal" not in df.columns:
        raise ValueError("DataFrame must contain a signal column")
    out = df.copy()
    col = f"fwd_return_{horizon_bars}"
    out[col] = pd.NA
    max_i = len(out) - 1
    for i, row in out.iterrows():
        sig = int(row.get("signal", 0))
        if sig not in (1, -1):
            continue
        entry_i = i + 1
        exit_i = i + horizon_bars
        if entry_i > max_i or exit_i > max_i:
            continue
        entry = float(out.at[entry_i, "open"])
        exit_ = float(out.at[exit_i, "close"])
        out.at[i, col] = (exit_ - entry) / entry if sig == 1 else (entry - exit_) / entry
    return out


def evaluate_multiple_horizons(df: pd.DataFrame, horizons: list[int]) -> pd.DataFrame:
    out = df.copy()
    for h in horizons:
        out = evaluate_forward_returns(out, int(h))
    return out


def summarize_forward_returns(df: pd.DataFrame, horizons: list[int]) -> list[dict[str, Any]]:
    total = int(df["signal"].isin([1, -1]).sum())
    longs = int((df["signal"] == 1).sum())
    shorts = int((df["signal"] == -1).sum())
    rows: list[dict[str, Any]] = []
    for h in horizons:
        col = f"fwd_return_{h}"
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
        s = df[col].dropna().astype(float)
        rows.append({
            "horizon": int(h),
            "signals_total": total,
            "long_signals": longs,
            "short_signals": shorts,
            "mean_forward_return": None if s.empty else float(s.mean()),
            "median_forward_return": None if s.empty else float(s.median()),
            "win_rate": None if s.empty else float((s > 0).mean()),
        })
    return rows


def build_trade_log(
    df: pd.DataFrame,
    horizons: list[int],
    symbol: str = "",
    timeframe: str = "",
    strategy: str = "",
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    max_i = len(df) - 1
    for i, row in df.iterrows():
        sig = int(row.get("signal", 0))
        if sig not in (1, -1):
            continue
        for h in horizons:
            entry_i = i + 1
            exit_i = i + int(h)
            if entry_i > max_i or exit_i > max_i:
                continue
            entry = float(df.at[entry_i, "open"])
            exit_ = float(df.at[exit_i, "close"])
            side = "long" if sig == 1 else "short"
            gross = (exit_ - entry) / entry if sig == 1 else (entry - exit_) / entry
            records.append({
                "symbol": symbol,
                "timeframe": timeframe,
                "strategy": strategy,
                "horizon": int(h),
                "entry_time": df.at[entry_i, "timestamp"] if "timestamp" in df.columns else entry_i,
                "exit_time": df.at[exit_i, "timestamp"] if "timestamp" in df.columns else exit_i,
                "side": side,
                "entry_price": entry,
                "exit_price": exit_,
                "gross_return": float(gross),
                "bars_held": int(h),
            })
    return pd.DataFrame.from_records(records)


def apply_cost_model(trades: pd.DataFrame, cost_params: dict[str, float]) -> pd.DataFrame:
    out = trades.copy()
    maker = float(cost_params.get("maker_fee_bps", 0.0))
    taker = float(cost_params.get("taker_fee_bps", 0.0))
    slippage = float(cost_params.get("slippage_bps", 0.0))
    round_trip_cost = (maker + taker + slippage) / 10000.0
    out["net_return"] = out["gross_return"] - round_trip_cost
    return out


def evaluate_trades(
    df: pd.DataFrame,
    horizons: list[int],
    cost_params: dict[str, float],
    symbol: str = "",
    timeframe: str = "",
    strategy: str = "",
) -> pd.DataFrame:
    trades = build_trade_log(df, horizons, symbol=symbol, timeframe=timeframe, strategy=strategy)
    return apply_cost_model(trades, cost_params)
