from __future__ import annotations

import math
import pandas as pd
from src.engine.trade_engine import evaluate_multiple_horizons, summarize_forward_returns, build_trade_log, apply_cost_model


def test_forward_returns_and_summary() -> None:
    df = pd.DataFrame({"timestamp":[0,1,2,3],"open":[100.0,110.0,105.0,100.0],"high":[110.0,112.0,106.0,103.0],"low":[99.0,108.0,103.0,98.0],"close":[110.0,105.0,100.0,102.0],"volume":[10,15,12,20],"signal":[1,0,-1,1],"score":[.1,0,-.05,.02]})
    out = evaluate_multiple_horizons(df, [1,2])
    rows = summarize_forward_returns(out, [1,2])
    assert len(rows) == 2
    assert rows[0]["signals_total"] == 3


def test_trade_log_and_cost_model() -> None:
    df = pd.DataFrame({"timestamp":[0,1,2],"open":[100.0,101.0,102.0],"close":[100.0,102.0,103.0],"signal":[1,0,0]})
    trades = build_trade_log(df, [1], symbol="BTCUSDT", timeframe="1m", strategy="test")
    assert len(trades) == 1
    net = apply_cost_model(trades, {"maker_fee_bps":1,"taker_fee_bps":1,"slippage_bps":1})
    assert "net_return" in net.columns
