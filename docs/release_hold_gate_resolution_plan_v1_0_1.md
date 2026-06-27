# Release HOLD Gate Resolution Plan v1.0.1

## Scope

This document records the current `main` status after the `v1.0.0` Release-GO Framework and defines the next conflict-free work sequence for moving the project from intentional `HOLD` toward evidence-backed `GO`.

The goal is not to force a release decision. The goal is to collect and validate the missing real-world evidence required by the existing release gate framework.

## Current main status

| Area | Status |
|---|---|
| Repository | Active |
| Default branch | `main` |
| Current framework | `v1.0.0` |
| Release decision model | Implemented |
| Correct current decision | `HOLD` |

The current framework is designed to return `HOLD` when critical real-world inputs are missing. This is correct behavior.

## CI / Actions status

The workflow on `main` defines the following required checks:

1. Editable package installation.
2. `compileall` over `src` and `scripts`.
3. `pytest -q` over the regression suite.
4. Deterministic sample data generation.
5. No-future-leak smoke check.
6. Data quality smoke check.
7. Pine export schema smoke check.
8. Multi-symbol walk-forward smoke check.
9. Forward reconciliation smoke check.
10. Release gate smoke check.

The workflow configuration exists and should be treated as the CI source of truth. Any new PR must keep this workflow green on Python 3.10, 3.11 and 3.12.

## Open gates blocking full GO

The current release gate framework identifies the following non-GO areas.

### P0 — Parity Gate

Status: `HOLD`.

Reason: Real TradingView diagnostic exports are required for each strategy. Synthetic fixture parity is not enough for release-level evidence.

Required evidence:

- Pine diagnostic CSV export per strategy.
- Matching Python mirror output for the same symbol, timeframe and bar range.
- Signal-bar match rate.
- Direction match rate.
- State / score / level mismatch summary.
- Critical mismatch count.

Minimum GO condition:

```text
signal_bar_match_rate = 100%
direction_match_rate = 100%
critical_mismatches = 0
```

### P0 — Real Bybit OHLCV Evidence

Status: not a separate HOLD in the default framework, but required for trustworthy parity and robustness evidence.

Required evidence:

- Real Bybit USDT perpetual OHLCV CSV files.
- UTC-normalized timestamps.
- Continuity report per symbol/timeframe.
- Duplicate timestamp check.
- Missing candle check.
- Non-positive price and negative volume checks.

Priority symbols:

```text
BTCUSDT
ETHUSDT
SOLUSDT
XRPUSDT
HYPEUSDT
```

Priority timeframes:

```text
3m
5m
15m
1h
```

### P1 — MTF Gate

Status: `SOFT-GO`.

Reason: Confirmed HTF helper exists, but real Pine `request.security()` parity remains required.

Required evidence:

- 3m -> 5m alignment parity.
- 5m -> 15m alignment parity.
- 5m -> 1h alignment parity.
- Comparison against Pine exports that explicitly include HTF fields.

Minimum GO condition:

```text
confirmed_htf_only = true
lookahead_mismatch_count = 0
htf_timestamp_mismatch_count = 0
```

### P1 — Real Multi-Symbol Robustness Gate

Status: `SOFT-GO`.

Reason: The runner exists, but current smoke evidence is sample-data based. Real market data is required before release-level robustness can be accepted.

Required evidence:

- At least five symbols evaluated.
- Long/short split included.
- Top-symbol profit share reported.
- Trade count threshold checked.
- Symbol-level positive / neutral / negative split reported.

Minimum GO condition:

```text
trade_count >= 80
positive_or_neutral_symbols >= 3 of 5
top_symbol_profit_share < 45%
```

### P1 — Forward Reconciliation Gate

Status: `SOFT-GO`.

Reason: Timestamp/direction reconciliation exists, but live or forward-shadow alert logs are still required.

Required evidence:

- Pine diagnostic export or TradingView alert log.
- Python forward-shadow output over the same bar interval.
- Reconciliation report for timestamp and direction.
- Open vs closed signal status for 3/5/10-bar follow-through.

Minimum GO condition:

```text
timestamp_match_rate = 100%
direction_match_rate = 100%
critical_mismatches = 0
```

## Recommended next branch sequence

### Branch 1 — Real input manifest and validation contract

Branch name:

```text
codex/real-input-manifest-v1-0-1
```

Deliverables:

- Add `configs/real_validation_inputs.example.yaml`.
- Add a manifest loader for expected data/export paths.
- Add tests for required symbol/timeframe/export fields.
- Add docs describing where real Bybit OHLCV and Pine exports must be placed.

Expected PR decision:

```text
SOFT-GO
```

### Branch 2 — Pine export evidence report

Branch name:

```text
codex/pine-export-evidence-v1-0-2
```

Deliverables:

- Extend export schema report with strategy/symbol/timeframe coverage summary.
- Add missing-field severity classification.
- Add Markdown output for export evidence.
- Add tests for incomplete and complete export sets.

Expected PR decision:

```text
SOFT-GO
```

### Branch 3 — Real parity evidence gate

Branch name:

```text
codex/real-parity-evidence-v1-0-3
```

Deliverables:

- Add per-strategy parity evidence runner.
- Add JSON and Markdown parity evidence reports.
- Add signal-bar, direction, state and score mismatch tables.
- Keep release decision as `HOLD` unless real evidence exists.

Expected PR decision:

```text
HOLD until real exports are supplied
```

### Branch 4 — Forward shadow evidence gate

Branch name:

```text
codex/forward-shadow-evidence-v1-0-4
```

Deliverables:

- Add forward-shadow evidence schema.
- Add 3/5/10-bar follow-through report.
- Add open/closed signal lifecycle state.
- Add reconciliation from TradingView alert/export to Python shadow rows.

Expected PR decision:

```text
SOFT-GO until live-forward evidence exists
```

## Required file placement

Real data should not be committed unless explicitly small and anonymized.

Use local paths matching this structure:

```text
data/raw/bybit/<symbol>/<timeframe>/*.csv
data/processed/<symbol>_<timeframe>.csv
data/pine_exports/<strategy>/<symbol>/<timeframe>/*.csv
reports/parity/<strategy>/<symbol>/<timeframe>/
reports/forward/<strategy>/<symbol>/<timeframe>/
```

`.gitignore` must continue to prevent accidental commits of large CSVs and generated reports.

## Next executable agent task

```text
Create branch codex/real-input-manifest-v1-0-1 from current main.
Implement configs/real_validation_inputs.example.yaml.
Implement a manifest validator that checks required symbols, timeframes and Pine export slots.
Add tests for complete and incomplete manifests.
Document the expected real-data placement.
Keep release decision HOLD until actual exports and real data are present.
Open a conflict-free PR against main.
```

## Release stance

Do not mark the project `GO` until the P0 Parity Gate has real TradingView diagnostic exports and zero critical mismatches.
