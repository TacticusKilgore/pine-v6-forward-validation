# Changelog

## Unreleased

- Added `docs/autonomous_agent_assignment_v1_0_0.md` as the autonomous implementation assignment for `v1.0.0 = Release-GO Framework`.
- Added README roadmap section for v1.0.0 release gates.
- Updated AGENTS.md to reference the active v1.0.0 release assignment.

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
