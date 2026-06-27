import pandas as pd

from src.engine.multi_symbol import evaluate_multi_symbol


def _frame():
    idx = pd.date_range("2026-01-01", periods=4, freq="5min", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100, 101, 102, 103],
            "high": [101, 102, 103, 104],
            "low": [99, 100, 101, 102],
            "close": [100, 101, 102, 103],
            "volume": [1000, 1000, 1000, 1000],
        },
        index=idx,
    )


def _signals(frame):
    out = frame.copy()
    out["atr"] = 1.0
    out["EXP_longSignal"] = False
    out["EXP_shortSignal"] = False
    out["EXP_entryPrice"] = float("nan")
    out["EXP_stopPrice"] = float("nan")
    return out


def test_multi_symbol_report_has_symbol_split():
    data = {symbol: _frame() for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "HYPEUSDT"]}
    report = evaluate_multi_symbol(data, "dummy", _signals)
    assert report.symbol_count == 5
    assert len(report.symbols) == 5
    assert report.positive_or_neutral_symbols == 5
