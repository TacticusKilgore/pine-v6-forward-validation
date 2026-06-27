from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from src.data.bybit_ohlcv_loader import load_bybit_ohlcv


def test_load_bybit_csv(tmp_path: Path) -> None:
    p = tmp_path / "BTCUSDT_1m.csv"
    pd.DataFrame({"timestamp":["2024-01-01T00:00:00Z"],"open":[1.0],"high":[1.2],"low":[0.9],"close":[1.1],"volume":[100]}).to_csv(p, index=False)
    df = load_bybit_ohlcv("BTCUSDT", "1m", live=False, data_dir=tmp_path)
    assert len(df) == 1


def test_load_bybit_live_without_ccxt(monkeypatch) -> None:
    import sys
    monkeypatch.setitem(sys.modules, "ccxt", None)
    with pytest.raises(ImportError):
        load_bybit_ohlcv("BTCUSDT", "1m", live=True)
