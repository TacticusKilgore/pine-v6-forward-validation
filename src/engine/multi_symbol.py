from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
import json

import pandas as pd

from src.engine.robustness import robust_score, trade_metrics
from src.engine.trade_engine import simulate_trades


@dataclass(frozen=True)
class SymbolEvaluation:
    symbol: str
    rows: int
    trade_count: float
    net_r_sum: float
    expectancy_r: float
    profit_factor: float
    win_rate: float
    max_drawdown_r: float
    long_trade_count: float
    short_trade_count: float
    long_expectancy_r: float
    short_expectancy_r: float
    robust_score: float


@dataclass(frozen=True)
class MultiSymbolReport:
    strategy: str
    symbol_count: int
    positive_or_neutral_symbols: int
    top_symbol_profit_share: float
    passed_min_symbols: bool
    passed_positive_symbols: bool
    passed_top_symbol_share: bool
    passed: bool
    symbols: list[SymbolEvaluation]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_multi_symbol(
    data_by_symbol: dict[str, pd.DataFrame],
    strategy_name: str,
    signal_fn: Callable[[pd.DataFrame], pd.DataFrame],
) -> MultiSymbolReport:
    rows: list[SymbolEvaluation] = []
    for symbol, frame in data_by_symbol.items():
        signals = signal_fn(frame)
        trades = simulate_trades(signals)
        metrics = trade_metrics(trades)
        rows.append(
            SymbolEvaluation(
                symbol=symbol,
                rows=int(len(frame)),
                trade_count=metrics["trade_count"],
                net_r_sum=metrics["net_r_sum"],
                expectancy_r=metrics["expectancy_r"],
                profit_factor=metrics["profit_factor"],
                win_rate=metrics["win_rate"],
                max_drawdown_r=metrics["max_drawdown_r"],
                long_trade_count=metrics["long_trade_count"],
                short_trade_count=metrics["short_trade_count"],
                long_expectancy_r=metrics["long_expectancy_r"],
                short_expectancy_r=metrics["short_expectancy_r"],
                robust_score=robust_score(metrics),
            )
        )
    positive = sum(1 for item in rows if item.net_r_sum >= 0)
    top_share = _top_symbol_profit_share(rows)
    passed_min_symbols = len(rows) >= 5
    passed_positive_symbols = positive >= 3
    passed_top_symbol_share = top_share < 0.45 if any(item.net_r_sum > 0 for item in rows) else False
    passed = passed_min_symbols and passed_positive_symbols and passed_top_symbol_share
    return MultiSymbolReport(
        strategy=strategy_name,
        symbol_count=len(rows),
        positive_or_neutral_symbols=positive,
        top_symbol_profit_share=top_share,
        passed_min_symbols=passed_min_symbols,
        passed_positive_symbols=passed_positive_symbols,
        passed_top_symbol_share=passed_top_symbol_share,
        passed=passed,
        symbols=rows,
    )


def write_multi_symbol_report(report: MultiSymbolReport, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _top_symbol_profit_share(rows: list[SymbolEvaluation]) -> float:
    positive = [max(0.0, item.net_r_sum) for item in rows]
    total = sum(positive)
    if total <= 0:
        return 0.0
    return float(max(positive) / total)
