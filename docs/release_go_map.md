# Release GO Map (v1.0.0)

This document tracks the release gates for `pine-v6-forward-validation` and defines the current evidence status for `v1.0.0`.

The release decision must remain `HOLD` until all critical gates have reproducible evidence. Fixture-based evidence is allowed for CI and development, but it must be explicitly labelled as fixture evidence and must not be represented as real market performance.

## Gate Status

| Gate | Status | Evidence |
|---|---:|---|
| Repository installability | GO | Package installs in CI through editable install. |
| Unit tests | GO | CI runs `pytest` across supported Python versions. |
| CI smoke gates | GO | CI runs compile, test, data-quality, export, parity, forward, reconciliation and release checks. |
| Pine diagnostic export schema | GO | Export-schema check and Pine export evidence report exist. |
| Bybit OHLCV schema | GO | OHLCV data-quality and schema validation path exists. |
| Real input manifest | GO | Manifest contract and validation CLI exist. |
| Pine-vs-Python parity report | SOFT-GO | Fixture path exists; real TradingView diagnostic exports are still required for final GO. |
| Forward-validation report | SOFT-GO | Fixture path exists; real signal evidence is still required for final GO. |
| Data-quality report | SOFT-GO | Sample and schema paths exist; real Bybit OHLCV evidence is still required. |
| Release decision | HOLD | Correct while real TradingView exports and real Bybit/OOS evidence are missing. |

## Critical GO Criteria

`v1.0.0` can be marked `GO` only when all of the following are true:

1. The repository installs cleanly from `main`.
2. Local tests and CI are green.
3. At least one Pine diagnostic export is imported and schema-valid.
4. At least one Bybit OHLCV dataset or validated import schema is available.
5. Pine-vs-Python parity report is generated.
6. Forward-validation report is generated.
7. Data-quality report is generated.
8. Reports are reproducible and machine-readable.
9. README documents the full workflow.
10. No critical HOLD gate remains unresolved.

## Remaining External Blockers

The remaining blockers are external evidence inputs, not missing framework mechanics:

- Real TradingView Pine-v6 diagnostic exports.
- Real or locally validated Bybit OHLCV files.
- Real parity evidence with zero critical mismatches.
- Real forward evidence over an explicit signal interval.

## Release Stance

Current stance:

```text
HOLD
```

Reason:

```text
Framework and fixture evidence are present, but real TradingView exports and real market-data evidence are still required for final GO.
```
