# AGENTS.md

## Mission

Maintain a Python validation harness for Pine Script v6 crypto-perpetual systems.

## Rules

1. Preserve chronological safety.
2. Keep Pine-parity logic separate from trade simulation.
3. Do not use centered rolling windows.
4. Do not use negative shifts for features.
5. Confirm HTF alignment before using higher-timeframe data.
6. Keep strategy modules deterministic.
7. Keep reports reproducible and caveated.

## Default market context

- Bybit USDT perpetuals
- BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, HYPEUSDT
- 1h / 15m / 5m / 3m validation stack
