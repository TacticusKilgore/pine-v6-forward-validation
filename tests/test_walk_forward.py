import pandas as pd

from src.engine.walk_forward import build_walk_forward_windows


def test_walk_forward_windows_build():
    idx = pd.date_range("2026-01-01", periods=24 * 60, freq="1h", tz="UTC")
    windows = build_walk_forward_windows(idx, train_days=10, validation_days=5, forward_days=5, step_days=5)
    assert len(windows) > 0
    assert windows[0].train_start < windows[0].forward_end
