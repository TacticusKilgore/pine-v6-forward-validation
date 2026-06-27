from __future__ import annotations

from pathlib import Path
import pandas as pd
from src.data.csv_loader import normalize_ohlcv


def fetch_bybit_ohlcv(symbol: str, timeframe: str = "5m", limit: int = 1000, out: str | Path | None = None) -> pd.DataFrame:
    try:
        import ccxt  # type: ignore
    except ImportError as exc:
        raise ImportError("Install live dependencies with: pip install -e .[live]") from exc
    exchange = ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    rows = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = normalize_ohlcv(df)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
    return df
