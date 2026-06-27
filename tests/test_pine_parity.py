import pandas as pd

from src.pine_parity.parity_checker import check_parity


def test_parity_checker_passes_identical_export():
    idx = pd.date_range("2026-01-01", periods=3, freq="5min", tz="UTC")
    df = pd.DataFrame({
        "timestamp": idx,
        "EXP_score": [1.0, 2.0, 3.0],
        "EXP_state": ["Neutral", "Active Long", "Neutral"],
        "EXP_entryPrice": [float("nan"), 100.0, float("nan")],
        "EXP_longSignal": [False, True, False],
        "EXP_shortSignal": [False, False, False],
    })
    result = check_parity(df, df)
    assert result.passed
    assert result.checked_rows == 3
