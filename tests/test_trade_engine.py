import pandas as pd

from src.engine.trade_engine import simulate_trades


def test_trade_engine_target_hit():
    idx = pd.date_range("2026-01-01", periods=4, freq="5min", tz="UTC")
    df = pd.DataFrame({
        "open": [100, 100, 101, 102],
        "high": [101, 102, 104, 104],
        "low": [99, 100, 101, 101],
        "close": [100, 101, 103, 102],
        "atr": [1, 1, 1, 1],
        "EXP_longSignal": [True, False, False, False],
        "EXP_shortSignal": [False, False, False, False],
        "EXP_entryPrice": [100.0, None, None, None],
        "EXP_stopPrice": [99.0, None, None, None],
    }, index=idx)
    trades = simulate_trades(df)
    assert len(trades) == 1
    assert trades.iloc[0]["reason"] == "target"
