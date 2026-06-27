# pine-v6-forward-validation

Repository for forward validation, Pine-v6 parity checks, walk-forward testing and shadow-forward evaluation of TradingView/Pine-derived crypto perpetual strategies.

## Purpose

This repo is designed to validate Pine Script v6 strategy logic outside TradingView with a reproducible Python harness:

1. **Pine parity**: replicate Pine-compatible indicators, MTF alignment and rolling-window behavior.
2. **Signal validation**: generate AMLR-X, IAX, IVSF and ELC signal streams from OHLCV candles.
3. **Forward validation**: evaluate signals on unseen chronological windows without optimization leakage.
4. **Robustness**: test parameter stability, cost sensitivity and walk-forward degradation.
5. **Shadow-forward**: ingest Pine exports or live OHLCV snapshots and compare expected vs. observed behavior.

## Default market assumptions

- Exchange orientation: Bybit USDT perpetuals.
- Primary validation symbols: BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, HYPEUSDT.
- Standard timeframe stack: 1h regime, 15m bias, 5m setup, 3m trigger.
- TradingView parity priority: no lookahead, no future leak, confirmed-bar-safe logic.

## Repository layout

```text
configs/       YAML configs for symbols, strategy defaults and validation defaults
data/          raw candles, processed candles and Pine CSV exports
src/data/      Bybit, CSV and resampling loaders
src/pine_parity/ Pine-compatible indicators, MTF alignment and parity checks
src/strategies/ Strategy signal modules
src/engine/    Signal, trade, cost, walk-forward and robustness engines
src/optimizers/ Grid/vectorbt optimizer interfaces
src/replay/    Backtrader replay adapter
src/reports/   Markdown/JSON report generators
scripts/       CLI entry points
tests/         Regression tests for leak safety, MTF, parity and engines
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev,live,replay,optimizer]
pytest
```

## Minimal workflow

```bash
python scripts/fetch_bybit_data.py --symbol BTC/USDT:USDT --timeframe 5m --limit 1000 --out data/raw/BTCUSDT_5m.csv
python scripts/run_walk_forward.py --data data/raw/BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml
python scripts/run_parity_check.py --left data/pine_exports/pine.csv --right data/processed/python.csv --out reports/parity/parity_report.md
```

## Validation rules

- Never optimize and evaluate on the same chronological segment.
- Never use incomplete HTF values as if they were confirmed unless explicitly marked as unsafe.
- Every signal module must be deterministic for a fixed OHLCV input and config.
- Pine exports are treated as the reference for signal parity only after timestamp normalization.
- Empty directories are represented by `.gitkeep` files because Git does not store empty folders.
