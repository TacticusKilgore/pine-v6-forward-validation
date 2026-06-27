# pine-v6-forward-validation

Production-oriented validation harness for Pine Script v6 trading projects.

## Mission

This repository validates TradingView/Pine-v6 strategy and indicator projects with a Python workflow that separates:

1. Pine signal parity
2. Repaint / future-leak checks
3. Walk-forward validation
4. Parameter robustness
5. Event-based trade replay
6. Forward shadow logging

The target market is Bybit USDT perpetuals, with the default stack:

- Regime: 1h
- Bias: 15m
- Setup: 5m
- Trigger: 3m

## Method Decision

| Layer | Tool | Role |
|---|---|---|
| Pine reference | TradingView Pine v6 | Source of truth for visual/signal logic |
| Parity | Custom Python harness | Bar-exact signal reproduction |
| Optimization | vectorbt / grid search | Parameter sweeps and robustness maps |
| Event replay | Backtrader adapter | Secondary order-lifecycle check |
| Forward | TradingView + Python shadow logger | Live/replay signal reconciliation |
| HFT / LOB | hftbacktest | Separate stack for GLFT / queue / market making |

## Current Version

`v0.2.0` hardens the initial scaffold into a usable local validation base:

- strict OHLCV schema normalization
- data-quality reporting
- no-future-leak / prefix-stability checks
- stricter Pine diagnostic parity checker
- frozen-parameter walk-forward evaluation
- JSON report writer
- deterministic sample data generator
- richer robustness metrics including long/short split

## Hard Rules

- No lookahead.
- No centered windows.
- No future HTF values.
- No optimization on forward windows.
- Confirmed-bar signal timing only.
- Pine diagnostic exports are treated as reference data.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Create deterministic sample data:

```bash
python scripts/make_sample_data.py \
  --rows 3500 \
  --out data/processed/sample_BTCUSDT_5m.csv
```

Run a no-future-leak / prefix-stability check:

```bash
python scripts/run_no_future_leak_check.py \
  --data data/processed/sample_BTCUSDT_5m.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml \
  --warmup-bars 250
```

Run a parity check against a TradingView diagnostic export:

```bash
python scripts/run_parity_check.py \
  --pine-export data/pine_exports/example_export.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml
```

Run walk-forward validation:

```bash
python scripts/run_walk_forward.py \
  --data data/processed/sample_BTCUSDT_5m.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml \
  --train-days 45 \
  --validation-days 15 \
  --forward-days 10 \
  --step-days 10 \
  --report-out reports/walk_forward/latest_walk_forward.json
```

Run a basic grid search:

```bash
python scripts/run_optimizer.py \
  --data data/processed/sample_BTCUSDT_5m.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml
```

## Pine Diagnostic Export Contract

Each Pine-v6 project should export at least these fields where possible:

```text
EXP_state
EXP_regime
EXP_bias
EXP_score
EXP_longSignal
EXP_shortSignal
EXP_longBlocker
EXP_shortBlocker
EXP_entryPrice
EXP_stopPrice
EXP_tp1
EXP_tp2
EXP_tp3
EXP_cooldown
EXP_invalidReason
```

Minimum parity columns currently enforced by default:

```text
EXP_longSignal
EXP_shortSignal
```

Python parity is valid only when signal time, direction, state, score and levels match within configured tolerances.

## Repository Layout

```text
configs/       YAML configuration for symbols, models and validation defaults
data/          raw candles, processed candles and TradingView diagnostic exports
src/data/      OHLCV loading, schema validation and resampling
src/pine_parity/ Pine-compatible indicators, rolling logic, MTF, parity and future-leak checks
src/strategies/ Python mirrors of Pine projects
src/engine/    signal, trade, cost, walk-forward and robustness engines
src/optimizers/ vectorbt and grid-search wrappers
src/replay/    Backtrader control replay adapter
src/reports/   JSON, summary, robustness and parity reports
tests/         regression checks for no future leak, MTF alignment and execution logic
scripts/       runnable CLI entry points
```

## Release Gate

A v6 project is forward-validation ready only when:

- Pine compiles without errors.
- Diagnostic export exists.
- Python harness reproduces Pine signals bar-exactly.
- MTF alignment is confirmed-bar safe.
- Prefix-stability / future-leak check passes.
- Walk-forward windows pass without parameter refit.
- At least five Bybit perps are tested separately.
- Long and short behavior is reported separately.
- Parameter neighborhood stability is acceptable.
- TradingView forward signals and Python shadow signals reconcile.

## Validation Status

Local smoke gate used for this repo state:

```text
pytest -q
10 passed

python -m compileall -q src scripts

python scripts/run_no_future_leak_check.py ...
passed=True checked_cutoffs=5 mismatches=0
```
