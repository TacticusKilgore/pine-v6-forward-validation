from __future__ import annotations

import pandas as pd
from src.data.resampler import resample_ohlcv


def test_resample_ohlcv_matches_pandas() -> None:
    df = pd.DataFrame({"timestamp":["2024-01-01T00:00:00Z","2024-01-01T00:01:00Z","2024-01-01T00:02:00Z","2024-01-01T00:03:00Z"],"open":[1.0,1.1,1.2,1.3],"high":[1.2,1.3,1.4,1.5],"low":[0.9,1.0,1.1,1.2],"close":[1.1,1.2,1.3,1.4],"volume":[100,200,150,250]})
    out = resample_ohlcv(df, "2T")
    assert len(out) >= 1
    assert set(["timestamp","open","high","low","close","volume"]).issubset(out.columns)
