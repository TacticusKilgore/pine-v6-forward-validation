import pandas as pd

from src.data.schema import infer_timeframe, normalize_ohlcv_frame, validate_ohlcv_frame


def test_normalize_and_validate_ohlcv_frame():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:05:00Z", "2026-01-01T00:00:00Z"],
            "open": [101, 100],
            "high": [102, 101],
            "low": [100, 99],
            "close": [101.5, 100.5],
            "volume": [10, 11],
        }
    )
    out = normalize_ohlcv_frame(df)
    report = validate_ohlcv_frame(out)
    assert report.passed
    assert report.rows == 2
    assert out.index.is_monotonic_increasing


def test_infer_timeframe():
    idx = pd.date_range("2026-01-01", periods=10, freq="5min", tz="UTC")
    assert infer_timeframe(idx) == "5min"
