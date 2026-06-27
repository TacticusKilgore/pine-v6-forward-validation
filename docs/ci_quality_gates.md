# CI Quality Gates

## Purpose

The CI workflow must block false release confidence. A passing workflow proves that the package installs, Python sources compile, tests pass and all required sample evidence commands can produce reports from deterministic fixtures.

CI smoke reports are not live performance evidence. They verify reproducibility and command integrity.

## Enforced checks

The workflow runs on Python 3.10, 3.11 and 3.12.

It enforces:

1. Editable package installation.
2. Python source compilation for `src` and `scripts`.
3. Full `pytest` suite.
4. Deterministic sample OHLCV generation.
5. No-future-leak smoke check.
6. Data-quality smoke report.
7. Pine export schema smoke report.
8. Real input manifest smoke report.
9. Pine export evidence smoke report.
10. Real parity evidence smoke report using a documented fixture export.
11. Forward validation evidence smoke report using a documented fixture.
12. Multi-symbol robustness smoke report.
13. Forward reconciliation smoke report.
14. Release gate smoke report.

## Fixture scope

The versioned fixture files are intentionally small and deterministic. They are not market-performance evidence.

Fixture evidence is allowed for CI because it proves that:

- CLI commands are executable.
- JSON and Markdown reports are generated.
- Schema validators reject malformed inputs.
- Parity and forward-evidence report builders can run without network access.

## Release stance

CI green is necessary but not sufficient for final `GO`.

The release remains blocked until real TradingView diagnostic exports and real or locally validated Bybit OHLCV inputs produce zero-critical-mismatch parity and forward-evidence reports.
