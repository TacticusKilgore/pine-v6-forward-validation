# Real Validation Inputs

## Purpose

The release framework must stay on `HOLD` until real TradingView diagnostic exports and real Bybit OHLCV evidence are available. Synthetic sample data is useful for CI smoke checks, but it is not sufficient for release-level parity evidence.

## Manifest

Use this template:

```text
configs/real_validation_inputs.example.yaml
```

Create a private local copy before running real checks:

```bash
cp configs/real_validation_inputs.example.yaml configs/real_validation_inputs.local.yaml
```

Do not commit local real-data manifests if they contain machine-specific paths.

## Required placement

Use this directory convention for real local inputs:

```text
data/raw/bybit/<symbol>/<timeframe>/<symbol>_<timeframe>.csv
data/pine_exports/<strategy>/<symbol>/<timeframe>/*.csv
reports/parity/<strategy>/<symbol>/<timeframe>/
reports/forward/<strategy>/<symbol>/<timeframe>/
```

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

Priority strategies:

```text
amlrx
iax
ivsf
elc
```

## Manifest validation

Check manifest coverage without requiring the referenced files to exist:

```bash
python scripts/run_real_input_manifest_check.py \
  --manifest configs/real_validation_inputs.example.yaml \
  --json-out reports/release/real_input_manifest_example.json
```

Check an actual local manifest and require files to exist:

```bash
python scripts/run_real_input_manifest_check.py \
  --manifest configs/real_validation_inputs.local.yaml \
  --require-existing-files \
  --json-out reports/release/real_input_manifest_local.json
```

## Release rule

A complete manifest is not a `GO` decision by itself. It only proves that the expected real inputs are declared. The project remains `HOLD` until the following evidence exists:

1. Data-quality reports pass for all required OHLCV files.
2. Pine export schema checks pass for all declared diagnostic exports.
3. Pine-vs-Python parity reports show zero critical mismatches.
4. Forward reconciliation reports show no timestamp or direction mismatches.
