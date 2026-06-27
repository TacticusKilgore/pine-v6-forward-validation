# Forward Validation Evidence Gate

## Purpose

The forward validation evidence gate measures causal follow-through after confirmed diagnostic signals. It is not a profitability claim. It is a reproducible evidence report for signal timing, direction and post-signal behavior.

The gate evaluates only data that exists after each signal. The future bars are labels/results, not features.

## Required input columns

```text
timestamp
open
high
low
close
volume
EXP_longSignal
EXP_shortSignal
```

Optional diagnostic columns:

```text
EXP_score
signal_state
EXP_state
risk_state
EXP_riskState
regime
EXP_regime
```

## Horizons

Default follow-through horizons:

```text
3
5
10
```

Each horizon is measured in bars of the input timeframe.

## Run

```bash
python scripts/run_forward_validation_evidence.py \
  --input data/processed/amlrx_BTCUSDT_5m_python.csv \
  --strategy amlrx \
  --symbol BTCUSDT \
  --timeframe 5m \
  --horizons 3 5 10 \
  --json-out reports/forward/amlrx/BTCUSDT/5m/forward_evidence.json \
  --md-out reports/forward/amlrx/BTCUSDT/5m/forward_evidence.md
```

## Output

The report contains:

- checked rows
- signal count
- per-signal follow-through after each horizon
- open/closed signal status
- long/short side summary
- regime summary when regime labels are present
- failure mode labels

## Failure mode labels

```text
follow_through_positive
follow_through_negative
flat
insufficient_future_bars
```

## Release stance

This gate can demonstrate that signal follow-through is reproducibly measured. It does not prove live profitability. The v1.0.0 release remains blocked until real Pine exports, real or validated Bybit OHLCV inputs, parity evidence and forward evidence are all present and reproducible.
