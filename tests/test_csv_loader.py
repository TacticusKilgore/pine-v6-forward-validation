from __future__ import annotations

import pandas as pd
import pytest

from src.data.csv_loader import load_csv, validate_ohlcv


def valid_df() -> pd.DataFrame:
    return pd.DataFrame({"timestamp":["2024-01-01T00:00:00Z","2024-01-01T00:01:00Z"],"open":[1.0,1.1],"high":[1.2,1.2],"low":[0.9,1.0],"close":[1.1,1.05],"volume":[100,200]})


def test_validate_ohlcv_valid_dataframe() -> None:
    validate_ohlcv(valid_df())


def test_validate_ohlcv_missing_column() -> None:
    df = valid_df().drop(columns=["close"])
    with pytest.raises(ValueError):
        validate_ohlcv(df)


def test_validate_ohlcv_negative_values() -> None:
    df = valid_df(); df.loc[0,"open"] = -1
    with pytest.raises(ValueError):
        validate_ohlcv(df)


def test_load_csv_and_validate(tmp_path) -> None:
    p = tmp_path / "ohlcv.csv"
    valid_df().to_csv(p, index=False)
    assert list(load_csv(p).columns) == ["timestamp","open","high","low","close","volume"]
