import pandas as pd

from src.engine.robustness import robust_score, side_metrics, trade_metrics


def test_trade_metrics_side_split():
    trades = pd.DataFrame(
        {
            "side": ["long", "short", "long"],
            "gross_r": [1.0, -1.0, 2.0],
            "net_r": [0.9, -1.1, 1.8],
        }
    )
    metrics = trade_metrics(trades)
    assert metrics["trade_count"] == 3
    assert metrics["long_trade_count"] == 2
    assert metrics["short_trade_count"] == 1
    assert robust_score(metrics) > 0
    assert set(side_metrics(trades)["side"]) == {"long", "short"}
