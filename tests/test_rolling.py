from __future__ import annotations

import numpy as np
import pandas as pd
from src.pine_parity.rolling import pine_sma, pine_ema, pine_rma, rolling_highest, rolling_lowest, rolling_sum, barssince


def test_pine_sma() -> None:
    s = pd.Series([1.0,2.0,3.0,4.0])
    r = pine_sma(s, 3)
    assert r.isna().iloc[0] and r.isna().iloc[1]
    assert r.iloc[2] == 2.0 and r.iloc[3] == 3.0


def test_pine_ema() -> None:
    r = pine_ema(pd.Series([1.0,2.0,3.0,4.0]), 3)
    assert np.isclose(r.iloc[1], 1.5)


def test_pine_rma() -> None:
    r = pine_rma(pd.Series([1.0,2.0,3.0,4.0]), 3)
    assert np.isclose(r.iloc[2], 2.0)


def test_rolling_highest_lowest_sum() -> None:
    s = pd.Series([1,4,2,5,3])
    assert rolling_highest(s,3).iloc[4] == 5
    assert rolling_lowest(s,3).iloc[4] == 2
    assert rolling_sum(s,3).iloc[4] == 10


def test_barssince() -> None:
    bs = barssince(pd.Series([False, False, True, False]))
    assert np.isnan(bs.iloc[0])
    assert bs.iloc[2] == 0
    assert bs.iloc[3] == 1
