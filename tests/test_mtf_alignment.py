import pandas as pd
from src.pine_parity.mtf import align_higher_timeframe


def test_mtf_alignment_previous_confirmed_row():
    ltf = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=4, freq="5min", tz="UTC")})
    htf = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=2, freq="15min", tz="UTC"), "x": [1, 2]})
    out = align_higher_timeframe(ltf, htf, ["x"], confirmed_only=True)
    assert pd.isna(out.loc[0, "x_htf"])
