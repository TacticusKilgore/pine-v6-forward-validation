from __future__ import annotations

import pandas as pd
import pytest
from src.engine.signal_engine import run_strategy


def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"timestamp":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],"open":[100.0]*21,"high":[101.0]*21,"low":[99.0]*21,"close":[100.5]*21,"volume":[10.0]*21})


@pytest.mark.parametrize("strategy", ["amlrx", "iax", "ivsf", "elc"])
def test_run_strategy_returns_required_columns(strategy: str) -> None:
    out = run_strategy(sample_df(), strategy, {})
    assert "signal" in out.columns
    assert "score" in out.columns
    assert len(out) == 21


def test_run_strategy_unknown_raises() -> None:
    with pytest.raises(ValueError):
        run_strategy(sample_df(), "unknown", {})
