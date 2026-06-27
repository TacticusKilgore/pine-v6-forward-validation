# AGENTS.md

## Mission

Build, audit, validate and maintain a Pine-v6 forward-validation harness for Bybit-oriented crypto perpetual projects.

The repository is not a generic backtester. Its purpose is to prove that Pine-v6 scripts can be reproduced, optimized and forward-validated in Python without repaint, future leak or hidden parameter overfit.

## Active Release Assignment

The current long-range implementation assignment is:

```text
docs/autonomous_agent_assignment_v1_0_0.md
```

Target:

```text
v1.0.0 = Release-GO Framework
```

All substantial patches should map to one of these gates:

- Data Gate
- Pine Export Gate
- Parity Gate
- No-Future-Leak Gate
- MTF Gate
- Walk-forward Gate
- Robustness Gate
- Release Decision Gate
- CI Gate
- Documentation Gate

## Operating Order

1. Diagnose
2. Structure
3. Implement
4. Validate
5. Report

## Non-Negotiable Rules

- Do not use future values.
- Do not use centered rolling windows.
- Do not silently shift signals to improve results.
- Do not optimize on the forward window.
- Do not merge long and short performance when validating an edge.
- Do not treat vectorbt or Backtrader output as valid unless Pine parity has already passed.
- Do not change default Bybit symbol sets without documenting the reason.

## Pine Parity Rules

Pine is the reference. Python is valid only if it reproduces the Pine diagnostic export.

Required checks:

- Timestamp equality
- Symbol equality where available
- Timeframe equality where available
- Signal direction equality
- Signal-bar equality
- State equality where exported
- Score tolerance check
- Entry, stop and target tolerance check
- MTF confirmed-bar alignment check
- Prefix-stability / no-future-leak check

## Data Rules

Expected OHLCV columns:

```text
timestamp, open, high, low, close, volume
```

Timestamps must be timezone-aware UTC or convertible to UTC.

OHLCV quality gate must fail on:

- missing price values
- non-positive OHLC prices
- negative volume
- duplicate timestamps after normalization
- non-DatetimeIndex validation input

## Validation Defaults

Default symbol set:

```text
BTCUSDT
ETHUSDT
SOLUSDT
XRPUSDT
HYPEUSDT
```

Default timeframes:

```text
1h regime
15m bias
5m setup
3m trigger
```

## Walk-forward Rules

- Parameter selection may inspect train and validation slices only.
- Forward slice must be evaluated with frozen parameters.
- Forward results must not feed back into the parameter set.
- Report train, validation and forward metrics separately.

## Reporting Rules

Every validation report must include:

- Net PnL or net R sum
- Expectancy
- Profit factor
- Max drawdown
- Win rate
- Average R
- Median R
- Trade count
- Long/short split
- Symbol split when available
- Regime split if available
- Parameter set
- Data interval
- Known limitations

## Implementation Style

- Prefer explicit functions over hidden framework magic.
- Keep indicator calculations Pine-compatible.
- Keep configuration in YAML.
- Keep scripts thin and logic inside `src/`.
- Add regression tests before changing parity, MTF or execution semantics.
- Direct script execution from repo root must work without package installation.
