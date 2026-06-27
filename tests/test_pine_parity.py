import pandas as pd
from src.pine_parity.parity_checker import compare_series


def test_parity_equal_series_passes():
    assert compare_series(pd.Series([1.0]), pd.Series([1.0]), "x").passed
