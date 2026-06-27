import pandas as pd

from src.pine_parity.mtf import confirmed_htf_series, assert_no_future_htf_leak


def test_confirmed_htf_series_alignment():
    idx = pd.date_range("2026-01-01", periods=48, freq="5min", tz="UTC")
    close = pd.Series(range(48), index=idx, dtype="float64")
    df = pd.DataFrame({"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1.0}, index=idx)
    aligned = confirmed_htf_series(df, "15min", lambda htf: htf["close"], shift_confirmed=True)
    assert aligned.index.equals(df.index)
    assert_no_future_htf_leak(df, aligned, "15min")
