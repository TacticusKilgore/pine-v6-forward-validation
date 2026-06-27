# pine-v6-forward-validation

Production-oriented validation harness for Pine Script v6 trading projects.

## Mission

This repository validates TradingView / Pine-v6 strategy and indicator projects with a Python workflow that separates Pine signal parity, repaint / future-leak checks, walk-forward validation, parameter robustness, event replay and forward shadow reconciliation.

Target market: Bybit USDT perpetuals.

Default stack:

- Regime: 1h
- Bias: 15m
- Setup: 5m
- Trigger: 3m

## Current Version

`v1.0.0` provides a Release-GO Framework. It can produce a clear project decision:

```text
GO
SOFT-GO
HOLD
NO-GO
```

The framework intentionally returns `HOLD` when critical real-world inputs are missing, such as TradingView diagnostic exports or real forward reconciliation data.

## Implemented Gates

- Data Quality Gate
- Pine Diagnostic Export Gate
- Pine-vs-Python Parity Gate
- No-Future-Leak / Repaint Gate
- MTF Confirmed-Bar Gate
- Walk-forward Gate
- Multi-Symbol Robustness Gate
- Forward Reconciliation Gate
- Release Decision Gate
- CI Gate
- Documentation Gate

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
pip install -e ".[dev]"
pytest -q
```

## Core Commands

Create deterministic sample data:

```bash
python scripts/make_sample_data.py --rows 3500 --out data/processed/sample_BTCUSDT_5m.csv
```

Run no-future-leak check:

```bash
python scripts/run_no_future_leak_check.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml --warmup-bars 250
```

Run data quality gate:

```bash
python scripts/run_data_quality.py --data data/processed/sample_BTCUSDT_5m.csv --symbol BTCUSDT --timeframe 5m --out reports/data_quality/sample_BTCUSDT_5m.json
```

Run export schema gate:

```bash
python scripts/run_export_schema_check.py --csv data/pine_exports/example_export_contract.csv --out reports/parity/example_export_schema.json
```

Run parity check:

```bash
python scripts/run_parity_check.py --pine-export data/pine_exports/example_export.csv --strategy amlrx --config configs/amlrx_v0_1.yaml
```

Run walk-forward validation:

```bash
python scripts/run_walk_forward.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml --report-out reports/walk_forward/latest_walk_forward.json
```

Run optimizer:

```bash
python scripts/run_optimizer.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml
```

Run release gate:

```bash
python scripts/run_release_gate.py --json-out reports/release/release_decision.json --md-out reports/release/release_decision.md
```

Run CI evidence smoke commands locally:

```bash
python scripts/run_real_input_manifest_check.py --manifest configs/real_validation_inputs.example.yaml --json-out reports/release/real_input_manifest_example.json
python scripts/run_pine_export_evidence.py --manifest configs/real_validation_inputs.example.yaml --json-out reports/parity/pine_export_evidence_example.json --md-out reports/parity/pine_export_evidence_example.md
python scripts/run_real_parity_evidence.py --pine-export data/pine_exports/example_export_contract.csv --python-output data/pine_exports/example_export_contract.csv --strategy fixture --symbol BTCUSDT --timeframe 5m --json-out reports/parity/fixture_parity_evidence.json --md-out reports/parity/fixture_parity_evidence.md
python scripts/run_forward_validation_evidence.py --input data/fixtures/forward_validation_fixture.csv --strategy fixture --symbol BTCUSDT --timeframe 5m --horizons 3 5 10 --json-out reports/forward/fixture_forward_evidence.json --md-out reports/forward/fixture_forward_evidence.md
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
docs/          release assignments, specs and implementation roadmaps
src/data/      OHLCV loading, schema validation and resampling
src/pine_parity/ Pine-compatible indicators, MTF, parity and future-leak checks
src/strategies/ Python mirrors of Pine projects
src/engine/    signal, trade, cost, walk-forward and robustness engines
src/optimizers/ vectorbt and grid-search wrappers
src/replay/    Backtrader adapter and forward reconciliation
src/reports/   JSON, Markdown and release decision reports
tests/         regression checks
scripts/       CLI entry points
```

## Release Requirement

A project is release-ready only when all critical gates pass. If Pine exports, real Bybit data, or forward reconciliation evidence are missing, the correct decision is `HOLD`, not `GO`.
