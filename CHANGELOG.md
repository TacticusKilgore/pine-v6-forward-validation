# Changelog

## Unreleased

- Added `docs/autonomous_agent_assignment_v1_0_0.md` as the autonomous implementation assignment for `v1.0.0 = Release-GO Framework`.
- Added README roadmap section for v1.0.0 release gates.
- Updated AGENTS.md to reference the active v1.0.0 release assignment.

## v1.0.0 - Release-GO Framework

- Added release decision engine with GO, SOFT-GO, HOLD and NO-GO states.
- Added `scripts/run_release_gate.py`.
- Added JSON and Markdown release decision outputs.
- Added default framework gate map.
- Added regression tests for release decisions.
- Extended CI with release gate smoke check.

## v0.5.0 - Forward shadow reconciliation

- Added timestamp and direction reconciliation for Pine exports and Python shadow outputs.
- Added `scripts/run_forward_reconciliation.py`.
- Added reconciliation JSON report output.
- Added regression tests for matching and mismatched signal directions.
- Extended CI with forward reconciliation smoke check.

## v0.4.0 - Multi-symbol walk-forward robustness

- Added multi-symbol evaluation report with symbol split.
- Added top-symbol profit-share robustness check.
- Added long/short split propagation in multi-symbol output.
- Added `scripts/run_multi_symbol_walk_forward.py`.
- Extended CI with multi-symbol smoke check.

## v0.3.0 - Real data and export contract gates

- Added OHLCV data quality report gate.
- Added Pine diagnostic export schema contract gate.
- Added CLI smoke commands for data quality and export schema checks.
- Extended CI with R1/R2 smoke checks.

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
