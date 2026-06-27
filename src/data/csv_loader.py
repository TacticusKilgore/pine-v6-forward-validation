from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_OHLCV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    missing = [col for col in REQUIRED_OHLCV_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    return out.loc[:, REQUIRED_OHLCV_COLUMNS].reset_index(drop=True)


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    return normalize_ohlcv(pd.read_csv(path))
