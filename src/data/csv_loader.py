from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.data.schema import normalize_ohlcv_frame, require_valid_ohlcv

REQUIRED_OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def load_ohlcv_csv(path: str | Path, *, validate: bool = True) -> pd.DataFrame:
    """Load OHLCV CSV and normalize timestamp/index semantics.

    Required columns: timestamp, open, high, low, close, volume.
    The returned DataFrame is indexed by UTC timestamp and sorted ascending.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"OHLCV CSV not found: {path}")

    df = pd.read_csv(path)
    out = normalize_ohlcv_frame(df)
    if validate:
        out = require_valid_ohlcv(out)
    return out


def save_ohlcv_csv(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    if isinstance(out.index, pd.DatetimeIndex):
        out = out.reset_index().rename(columns={out.index.name or "index": "timestamp"})
    out.to_csv(path, index=False)
