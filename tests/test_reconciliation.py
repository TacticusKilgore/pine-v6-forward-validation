import pandas as pd

from src.replay.reconciliation import reconcile_signal_frames


def test_reconciliation_passes_matching_directions():
    pine = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z", "2026-01-01T00:05:00Z"],
            "EXP_longSignal": [False, True],
            "EXP_shortSignal": [False, False],
        }
    )
    shadow = pine.copy()
    report = reconcile_signal_frames(pine, shadow)
    assert report.passed
    assert report.signal_mismatches == 0
    assert report.direction_match_rate == 1.0


def test_reconciliation_detects_mismatch():
    pine = pd.DataFrame(
        {"timestamp": ["2026-01-01T00:00:00Z"], "EXP_longSignal": [True], "EXP_shortSignal": [False]}
    )
    shadow = pd.DataFrame(
        {"timestamp": ["2026-01-01T00:00:00Z"], "EXP_longSignal": [False], "EXP_shortSignal": [True]}
    )
    report = reconcile_signal_frames(pine, shadow)
    assert not report.passed
    assert report.signal_mismatches == 1
