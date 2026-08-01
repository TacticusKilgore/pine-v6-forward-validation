from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

REQUIRED_SIGNAL_COLUMNS = {"event_id", "bar_time_utc", "direction", "entry_price"}
REQUIRED_CANDLE_COLUMNS = {"timestamp", "open", "high", "low", "close"}


def _first_hit(
    window: pd.DataFrame,
    direction: str,
    stop: float | None,
    targets: list[float],
) -> str:
    for _, bar in window.iterrows():
        high, low = float(bar["high"]), float(bar["low"])
        stop_hit = stop is not None and (
            low <= stop if direction == "LONG" else high >= stop
        )
        target_hits = [
            index + 1
            for index, target in enumerate(targets)
            if (high >= target if direction == "LONG" else low <= target)
        ]
        if stop_hit and target_hits:
            return "AMBIGUOUS_SAME_BAR"
        if stop_hit:
            return "STOP"
        if target_hits:
            return f"TP{max(target_hits)}"
    return "NONE"


def resolve_signal_outcomes(
    signals: pd.DataFrame,
    candles: pd.DataFrame,
    horizons: Iterable[int] = (1, 3, 5, 10),
) -> pd.DataFrame:
    missing_signals = REQUIRED_SIGNAL_COLUMNS - set(signals.columns)
    missing_candles = REQUIRED_CANDLE_COLUMNS - set(candles.columns)
    if missing_signals:
        raise ValueError(f"missing signal columns: {sorted(missing_signals)}")
    if missing_candles:
        raise ValueError(f"missing candle columns: {sorted(missing_candles)}")

    candle_df = candles.copy()
    candle_df["timestamp"] = pd.to_datetime(candle_df["timestamp"], utc=True)
    candle_df = (
        candle_df.sort_values("timestamp")
        .drop_duplicates("timestamp", keep="last")
        .reset_index(drop=True)
    )
    resolved_horizons = tuple(sorted({int(value) for value in horizons if int(value) > 0}))
    max_horizon = max(resolved_horizons)
    results: list[dict] = []

    for _, signal in signals.iterrows():
        direction = str(signal["direction"]).upper()
        if direction not in {"LONG", "SHORT"}:
            raise ValueError(f"invalid direction: {direction}")
        signal_time = pd.to_datetime(signal["bar_time_utc"], utc=True)
        future = candle_df[candle_df["timestamp"] > signal_time].head(max_horizon)
        entry = float(signal["entry_price"])
        sign = 1.0 if direction == "LONG" else -1.0
        row: dict = {"event_id": signal["event_id"], "resolved_bars": int(len(future))}

        for horizon in resolved_horizons:
            if len(future) >= horizon:
                close = float(future.iloc[horizon - 1]["close"])
                row[f"return_{horizon}_bars"] = sign * (close - entry) / entry
            else:
                row[f"return_{horizon}_bars"] = np.nan

        if len(future):
            favorable = (
                future["high"] - entry
                if direction == "LONG"
                else entry - future["low"]
            )
            adverse = (
                entry - future["low"]
                if direction == "LONG"
                else future["high"] - entry
            )
            row["mfe_price"] = float(favorable.max())
            row["mae_price"] = float(adverse.max())
            row["bars_to_mfe"] = int(favorable.to_numpy().argmax()) + 1
            row["bars_to_mae"] = int(adverse.to_numpy().argmax()) + 1
            stop = signal.get("invalidation_level")
            stop = None if pd.isna(stop) else float(stop)
            targets = [
                float(signal[column])
                for column in ("target_1", "target_2", "target_3")
                if column in signal.index and not pd.isna(signal[column])
            ]
            row["first_touch"] = _first_hit(future, direction, stop, targets)
            risk = abs(entry - stop) if stop is not None else np.nan
            row["mfe_r"] = row["mfe_price"] / risk if risk and not np.isnan(risk) else np.nan
            row["mae_r"] = row["mae_price"] / risk if risk and not np.isnan(risk) else np.nan
        else:
            row.update(
                {
                    "mfe_price": np.nan,
                    "mae_price": np.nan,
                    "bars_to_mfe": np.nan,
                    "bars_to_mae": np.nan,
                    "first_touch": "UNRESOLVED",
                    "mfe_r": np.nan,
                    "mae_r": np.nan,
                }
            )
        results.append(row)

    return pd.DataFrame(results)
