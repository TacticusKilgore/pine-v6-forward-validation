from __future__ import annotations

import pandas as pd
from src.pine_parity.mtf import align_htf_to_ltf


def test_align_htf_to_ltf_adds_columns() -> None:
    ltf = pd.DataFrame({"timestamp": pd.to_datetime(["2024-01-01T00:00:00Z","2024-01-01T00:01:00Z","2024-01-01T00:02:00Z","2024-01-01T00:03:00Z"], utc=True), "value": [1,2,3,4]})
    htf = pd.DataFrame({"timestamp": pd.to_datetime(["2024-01-01T00:01:00Z","2024-01-01T00:03:00Z"], utc=True), "htf_value": [10,20]})
    out = align_htf_to_ltf(ltf, htf, confirmed_only=True, columns=["htf_value"])
    assert len(out) == len(ltf)
    assert "htf_value_htf" in out.columns
    assert out["htf_value_htf"].isna().iloc[0]
    assert out["htf_value_htf"].isna().iloc[1]
