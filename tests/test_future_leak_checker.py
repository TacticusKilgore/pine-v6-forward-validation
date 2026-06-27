import pandas as pd
import pytest

from src.pine_parity.future_leak import assert_prefix_stability


def sample_df(n=80):
    idx = pd.date_range("2026-01-01", periods=n, freq="5min", tz="UTC")
    close = pd.Series(range(100, 100 + n), index=idx, dtype="float64")
    return pd.DataFrame(
        {"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1000.0},
        index=idx,
    )


def test_prefix_stability_passes_for_past_only_signal():
    def run_fn(df):
        out = df.copy()
        out["signal"] = out["close"] > out["close"].rolling(10, min_periods=10).mean()
        return out

    report = assert_prefix_stability(run_fn, sample_df(), ["signal"], warmup_bars=15)
    assert report.passed


def test_prefix_stability_fails_for_future_shift():
    def run_fn(df):
        out = df.copy()
        out["signal"] = out["close"].shift(-1) > out["close"]
        return out

    report = assert_prefix_stability(run_fn, sample_df(), ["signal"], warmup_bars=5)
    assert not report.passed
    assert report.mismatches
