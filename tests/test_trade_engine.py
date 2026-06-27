import pandas as pd
from src.engine.trade_engine import evaluate_forward_returns


def test_trade_engine_adds_forward_return():
    df = pd.DataFrame({"open": [1, 1, 1], "close": [1, 2, 3], "signal": [1, 0, 0]})
    assert "forward_return" in evaluate_forward_returns(df, 1).columns
