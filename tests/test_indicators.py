from __future__ import annotations

import numpy as np
import pandas as pd

from src.pine_parity.indicators import hlc3, true_range, atr, vwap_sessionless, body_size, upper_wick, lower_wick, close_location, body_efficiency


def test_basic_indicators() -> None:
    o = pd.Series([8.5, 9.5]); h = pd.Series([10.0, 11.0]); l = pd.Series([8.0, 9.0]); c = pd.Series([9.0, 10.0]); v = pd.Series([100.0, 150.0])
    assert np.isclose(hlc3(h,l,c).iloc[0], 9.0)
    assert np.isclose(true_range(h,l,c).iloc[1], 2.0)
    assert np.isclose(atr(h,l,c,2).iloc[1], 2.0)
    assert np.isclose(vwap_sessionless(h,l,c,v).iloc[0], 9.0)
    assert np.isclose(body_size(o,c).iloc[0], 0.5)
    assert np.isclose(upper_wick(o,h,c).iloc[0], 1.0)
    assert np.isclose(lower_wick(o,l,c).iloc[0], 0.5)
    assert np.isclose(close_location(h,l,c).iloc[0], 0.5)
    assert np.isclose(body_efficiency(h,l,o,c).iloc[0], 0.25)
