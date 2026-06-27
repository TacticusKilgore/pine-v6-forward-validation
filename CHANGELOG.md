# Changelog

## v0.2.1 - CI packaging hardening

- Added runtime dependencies to `pyproject.toml` so editable installs work in clean environments.
- Added explicit `dev`, `live`, `replay`, `optimizer` and `all` extras.
- Updated GitHub Actions to compile sources before tests.
- Added CI sample-data generation and no-future-leak smoke check.
- Clarified `requirements.txt` dependency groups.

## v0.2.0 - Forward-validation hardening

- Added strict OHLCV normalization and data-quality reporting.
- Added deterministic sample OHLCV generator for smoke tests.
- Added prefix-stability future-leak checker for Pine-parity outputs.
- Hardened parity checker with required diagnostic columns and signal-bar matching.
- Added richer trade/robustness metrics with long/short split.
- Added frozen-parameter walk-forward evaluation object and JSON report output.
- Added CLI script for no-future-leak checks.
- Added regression tests for schema, future-leak detection and robustness metrics.
- Fixed direct script execution by injecting repo root into `sys.path`.

## v0.1.0 - Initial scaffold

- Added Pine-v6 forward-validation repository structure.
- Added AMLR-X, IAX, IVSF and ELC Python mirror placeholders.
- Added core data, parity, trade, optimization, replay and reporting modules.
- Added first regression test set.
