from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .cost_model import CostModel


@dataclass(frozen=True)
class TradeEngineConfig:
    stop_atr_mult: float = 0.65
    target_rr: float = 1.8
    timeout_bars: int = 24
    risk_per_trade_fraction: float = 0.008


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str
    entry: float
    stop: float
    target: float
    exit: float
    gross_r: float
    net_r: float
    reason: str


def simulate_trades(
    signals: pd.DataFrame,
    config: TradeEngineConfig | None = None,
    costs: CostModel | None = None,
) -> pd.DataFrame:
    """Simple one-position-at-a-time OHLC trade simulator.

    Assumption when stop and target are both touched in the same candle: stop first.
    This is conservative for intrabar uncertainty.
    """
    config = config or TradeEngineConfig()
    costs = costs or CostModel()
    trades: list[Trade] = []
    in_pos = False
    side = ""
    entry = stop = target = risk = np.nan
    entry_time = None
    bars_in_pos = 0

    for ts, row in signals.iterrows():
        long_sig = bool(row.get("EXP_longSignal", False))
        short_sig = bool(row.get("EXP_shortSignal", False))
        atr = float(row.get("atr", np.nan))

        if not in_pos:
            if long_sig or short_sig:
                raw_entry = float(row.get("EXP_entryPrice", row["close"]))
                side = "long" if long_sig else "short"
                entry = costs.apply_entry_long(raw_entry) if side == "long" else costs.apply_entry_short(raw_entry)
                if "EXP_stopPrice" in signals.columns and not pd.isna(row.get("EXP_stopPrice")):
                    stop = float(row.get("EXP_stopPrice"))
                else:
                    stop = entry - atr * config.stop_atr_mult if side == "long" else entry + atr * config.stop_atr_mult
                risk = abs(entry - stop)
                if risk <= 0 or pd.isna(risk):
                    continue
                target = entry + risk * config.target_rr if side == "long" else entry - risk * config.target_rr
                entry_time = ts
                bars_in_pos = 0
                in_pos = True
            continue

        bars_in_pos += 1
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        exit_price = None
        reason = ""

        if side == "long":
            if low <= stop:
                exit_price = stop
                reason = "stop"
            elif high >= target:
                exit_price = target
                reason = "target"
            elif bars_in_pos >= config.timeout_bars:
                exit_price = close
                reason = "timeout"
            if exit_price is not None:
                gross_r = (exit_price - entry) / risk
        else:
            if high >= stop:
                exit_price = stop
                reason = "stop"
            elif low <= target:
                exit_price = target
                reason = "target"
            elif bars_in_pos >= config.timeout_bars:
                exit_price = close
                reason = "timeout"
            if exit_price is not None:
                gross_r = (entry - exit_price) / risk

        if exit_price is not None and entry_time is not None:
            net_r = gross_r - costs.round_trip_bps / 10_000.0 / config.risk_per_trade_fraction
            trades.append(
                Trade(
                    entry_time=entry_time,
                    exit_time=ts,
                    side=side,
                    entry=entry,
                    stop=stop,
                    target=target,
                    exit=float(exit_price),
                    gross_r=float(gross_r),
                    net_r=float(net_r),
                    reason=reason,
                )
            )
            in_pos = False
            side = ""
            entry_time = None

    return pd.DataFrame([t.__dict__ for t in trades])
