import pandas as pd

from src.data.data_quality_gate import build_data_quality_report


def test_data_quality_gate_passes_continuous_ohlcv():
    idx = pd.date_range("2026-01-01", periods=5, freq="5min", tz="UTC")
    df = pd.DataFrame(
        {
            "timestamp": idx,
            "open": [100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 100, 101, 102, 103],
            "close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "volume": [1000, 1001, 1002, 1003, 1004],
        }
    )
    report = build_data_quality_report(df, "BTCUSDT", "5m")
    assert report.passed
    assert report.missing_candles == 0
