from __future__ import annotations

import pandas as pd
from src.pine_parity.parity_checker import compare_series, compare_signals, parity_check


def test_compare_series() -> None:
    r = compare_series(pd.Series([1.0,2.0,3.0]), pd.Series([1.0,2.005,3.1]), tol=0.01)
    assert r["mismatches"] == 1
    assert r["total"] == 3
    assert abs(r["max_error"] - 0.1) < 1e-6


def test_compare_signals() -> None:
    assert compare_signals(pd.Series([1,0,-1]), pd.Series([1,1,-1]))["mismatches"] == 1


def test_parity_check() -> None:
    a = pd.DataFrame({"x":[1.0,2.0], "s":["a","b"]})
    b = pd.DataFrame({"x":[1.0,2.2], "s":["a","c"]})
    report = parity_check(a, b, ["x","s"], tol=0.05)
    assert report["x"]["mismatches"] == 1
    assert report["s"]["mismatches"] == 1
