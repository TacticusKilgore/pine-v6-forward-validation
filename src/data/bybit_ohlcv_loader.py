from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pandas as pd


@dataclass(frozen=True)
class BybitOHLCVRequest:
    symbol: str
    timeframe: str
    since_ms: int | None = None
    limit: int = 1000


class BybitOHLCVLoader:
    """Thin CCXT loader for Bybit OHLCV.

    The class is intentionally small. Production workflows should persist raw responses
    and validate continuity before using data in walk-forward tests.
    """

    def __init__(self, enable_rate_limit: bool = True) -> None:
        try:
            import ccxt  # type: ignore
        except ImportError as exc:
            raise ImportError("Install ccxt to use BybitOHLCVLoader") from exc
        self.exchange = ccxt.bybit({"enableRateLimit": enable_rate_limit})

    def fetch(self, request: BybitOHLCVRequest) -> pd.DataFrame:
        rows = self.exchange.fetch_ohlcv(
            request.symbol,
            timeframe=request.timeframe,
            since=request.since_ms,
            limit=request.limit,
        )
        df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df.set_index("timestamp").sort_index()

    def fetch_many(self, requests: Iterable[BybitOHLCVRequest]) -> dict[str, pd.DataFrame]:
        return {f"{r.symbol}_{r.timeframe}": self.fetch(r) for r in requests}
