import pandas as pd

from src.pine_parity.indicators import atr, ema


def sample_df(n=120):
    idx = pd.date_range("2026-01-01", periods=n, freq="5min", tz="UTC")
    close = pd.Series(range(100, 100 + n), index=idx, dtype="float64")
    return pd.DataFrame({
        "open": close - 0.5,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0,
    }, index=idx)


def test_indicator_prefix_stability():
    df_full = sample_df(120)
    df_prefix = df_full.iloc[:80]
    full_ema = ema(df_full["close"], 20).iloc[:80]
    prefix_ema = ema(df_prefix["close"], 20)
    pd.testing.assert_series_equal(full_ema, prefix_ema)

    full_atr = atr(df_full, 14).iloc[:80]
    prefix_atr = atr(df_prefix, 14)
    pd.testing.assert_series_equal(full_atr, prefix_atr)
