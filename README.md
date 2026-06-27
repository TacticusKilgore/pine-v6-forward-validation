# pine-v6-forward-validation

Forward-validation repository for Pine Script v6 strategy projects.

## Scope

- Pine-v6 parity checks
- Bybit perpetual OHLCV ingestion
- AMLR-X / IAX / IVSF / ELC signal modules
- Walk-forward validation
- Robustness checks
- Forward-shadow reporting

## Default stack

- Exchange: Bybit USDT perpetuals
- Regime: 1h
- Bias: 15m
- Setup: 5m
- Trigger: 3m
- Validation: no future leak, confirmed HTF only, chronological train/test split

## Quick start

```bash
python -m venv .venv
pip install -e .[dev,live,replay,optimizer]
pytest
```

Empty folders are materialized with `.gitkeep`.
