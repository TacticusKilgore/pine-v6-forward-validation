import pandas as pd

from src.pine_parity.export_contract import normalize_export_frame, validate_export_contract


def test_export_contract_passes_full_fixture():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z"],
            "symbol": ["BTCUSDT"],
            "timeframe": ["5m"],
            "EXP_state": ["Neutral"],
            "EXP_regime": ["Range"],
            "EXP_bias": ["Neutral"],
            "EXP_score": [0],
            "EXP_longSignal": ["false"],
            "EXP_shortSignal": ["0"],
            "EXP_longBlocker": ["none"],
            "EXP_shortBlocker": ["none"],
            "EXP_entryPrice": [0],
            "EXP_stopPrice": [0],
            "EXP_tp1": [0],
            "EXP_tp2": [0],
            "EXP_tp3": [0],
            "EXP_cooldown": [0],
            "EXP_invalidReason": ["none"],
        }
    )
    report = validate_export_contract(df)
    assert report.passed
    assert report.missing_required_columns == []


def test_export_contract_fills_missing_view():
    normalized = normalize_export_frame(pd.DataFrame({"timestamp": ["2026-01-01T00:00:00Z"]}))
    assert "EXP_longSignal" in normalized.columns
    assert normalized.loc[0, "EXP_longSignal"] == False
