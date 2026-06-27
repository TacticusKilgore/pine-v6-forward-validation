# AUTONOMER AGENTENAUFTRAG

## Projekt

`TacticusKilgore/pine-v6-forward-validation`

## Zielversion

`v1.0.0 = Release-GO Framework`

## Rolle

Agiere als autonomer Senior Python Quant Validation Engineer, Pine-v6-Parity-Architekt, Forward-Validation-Designer, CI-/Packaging-Gatekeeper, GitHub-Repo-Operator und Release-Engineer.

Arbeite eigenständig. Rückfragen sind nur erlaubt, wenn ein echter Blocker besteht, der nicht durch Repository-Inspektion, Tests, konservative technische Entscheidungen oder bestehende Projektregeln lösbar ist.

## Mission

Baue das Repository von der v0.2.x-Basis zu einem produktionsnahen Release-Gate-Framework aus. Das Framework muss für Pine-v6-Projekte reproduzierbar prüfen, ob Python-Signale bar-genau mit Pine-Diagnostic-Exports übereinstimmen, ob kein Repaint/Lookahead/Future-Leak vorliegt, ob Bybit-Perp-OHLCV-Daten sauber verarbeitet werden, ob Walk-forward-Validierung ohne Forward-Optimierung möglich ist und ob am Ende `GO`, `SOFT-GO`, `HOLD` oder `NO-GO` ausgegeben wird.

## Arbeitsreihenfolge

1. Inspect
2. Diagnose
3. Patch
4. Test
5. Report
6. Commit / PR / Merge, falls möglich

## Nicht verhandelbare Regeln

- Keine Future-Leaks, kein Lookahead, kein Repaint akzeptieren.
- Keine centered rolling windows.
- Keine negativen Shifts für Features oder Signale.
- Keine Optimierung auf Forward-Ergebnisse.
- Keine Tests entfernen, um grün zu werden.
- Keine kosmetischen Änderungen ohne Validierungsnutzen.
- Pine-Parity, Backtest, Optimierung und Forward-Test strikt trennen.
- Long/Short, Symbol, Regime und Session getrennt auswerten.

## Aktueller Stand

```text
v0.2.0 = Repo-Basis GO
v0.2.1 = CI-/Packaging-Hardening vorbereitet
```

Nächste Pflichtstufe ist v0.2.1 mit `pyproject.toml` Dependencies, Extras `dev/live/replay/optimizer/all`, erweitertem GitHub-Actions-Smoke-Gate und Merge nach `main`.

## Zielbild v1.0.0

### Data Gate

Pflichtfunktionen: Bybit-OHLCV-Loader, CSV-Loader, UTC-Timestamp-Normalisierung, OHLCV-Schema-Gate, Duplicate-Erkennung, Missing-Candle-Erkennung, Gap-Report, non-positive-price Gate, negative-volume Gate, Timeframe-Inferenz und Resampling für 1m/3m/5m/15m/1h.

Pflichtoutput: `data_quality_report.json` mit `symbol`, `timeframe`, `rows`, `start`, `end`, `missing_candles`, `duplicate_timestamps`, `non_positive_prices`, `negative_volume`, `inferred_timeframe`, `passed`.

### Pine Export Gate

Implementiere einen stabilen Diagnostic Export Contract mit diesen Kernfeldern: `timestamp`, `symbol`, `timeframe`, `EXP_state`, `EXP_regime`, `EXP_bias`, `EXP_score`, `EXP_longSignal`, `EXP_shortSignal`, `EXP_longBlocker`, `EXP_shortBlocker`, `EXP_entryPrice`, `EXP_stopPrice`, `EXP_tp1`, `EXP_tp2`, `EXP_tp3`, `EXP_cooldown`, `EXP_invalidReason`.

Fehlende Pflichtfelder müssen explizit gemeldet werden. Optionalfelder werden als `not_available` markiert. Timestamps sind UTC-normalisiert. Pine-Bools müssen robust als `true/false`, `1/0`, `yes/no` geparst werden.

### Parity Gate

Die Parity Engine muss Signal-Bar-Matching, Direction-Matching, State-Matching, Score-Toleranz, Entry/Stop/TP-Toleranz in BPS, Missing-Column-Report, Extra-Column-Report, Mismatch-CSV, Summary-JSON und Markdown-Report liefern.

GO-Kriterium: `signal_bar_match_rate = 100%`, `direction_match_rate = 100%`, `critical_mismatches = 0`.

### No-Future-Leak Gate

Implementiere harte Checks für Prefix-Stability, negative-shift detection, centered rolling detection, non-confirmed HTF use, timestamp misalignment, signal-after-outcome leakage und accidental label leakage.

GO-Kriterium: `passed=True`, `checked_cutoffs >= 5`, `mismatches=0`.

### MTF Gate

Baue confirmed-bar-sichere MTF-Komponenten für 1h Regime, 15m Bias, 5m Setup und 3m Trigger. Tests müssen 3m->5m, 5m->15m und 5m->1h prüfen. Dokumentiere, wie Pine `request.security()` gespiegelt wird.

### Strategy Mirror Gate

Baue Pine-nahe Python-Mirror für AMLR-X, IAX, IVSF und ELC. Priorität: AMLR-X, IAX, IVSF, ELC. Jedes Modul muss `EXP_state`, `EXP_score`, `EXP_longSignal`, `EXP_shortSignal`, `EXP_entryPrice`, `EXP_stopPrice`, `EXP_tp1` erzeugen und deterministisch sein.

### Trade Engine Gate

Die Trade Engine muss one-position-at-a-time, Long/Short-Split, configurable entry timing, Stop, TP1/TP2/TP3, Timeout, Fees, Slippage, R-Multiple, conservative intrabar rule und optional partial exits unterstützen.

Pflichtmetriken: `trade_count`, `net_r_sum`, `gross_r_sum`, `expectancy_r`, `profit_factor`, `win_rate`, `avg_r`, `median_r`, `max_drawdown_r`, `long_trade_count`, `short_trade_count`, `long_expectancy_r`, `short_expectancy_r`.

### Walk-forward Gate

Train, Validation und Forward müssen getrennt sein. Standard: 45 Tage Train, 15 Tage Validation, 10 Tage Forward, 10 Tage Step. Parameter dürfen nur aus Train/Validation stammen. Jeder Forward-Run gibt einen Frozen-Parameter-Hash aus.

Pflichtoutput: `walk_forward_report.json` und `walk_forward_summary.md`.

### Optimizer Gate

Implementiere `grid_search` als Pflichtmodus und `vectorbt_optional` als optionale Erweiterung. Optimizer dürfen nie direkt auf Forward-Fenster optimieren. Pflicht: Parameter Grid, Objective Function, RobustScore, Parameter-Neighborhood-Stability, Top-N Configs und Reject unstable parameter islands.

### Robustness Gate

Kriterien: Trade Count >= 80, mindestens 3 von 5 Symbole positiv oder neutral, Top-Symbol Profit Share < 45%, Long/Short getrennt geprüft, Forward-Degradation akzeptabel, Parameter-Neighborhood-Stability akzeptabel, keine isolierte Parameterinsel.

Standard-Symbole: BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, HYPEUSDT. Standard-Timeframes: 1h, 15m, 5m, 3m.

### Release Decision Gate

Implementiere `GO`, `SOFT-GO`, `HOLD`, `NO-GO`.

`GO`: alle kritischen Gates bestanden, Parity vollständig, No-Future-Leak bestanden, Walk-forward robust, Long/Short/Symbol-Splits akzeptabel.

`SOFT-GO`: Kernlogik stabil, kleinere nichtkritische Lücken, nur für weitere Forward-Beobachtung.

`HOLD`: fehlende Daten, fehlende Exports, schwache Robustheit oder unvollständige Validierung.

`NO-GO`: Future-Leak, Repaint, schwere Parity-Abweichung, instabile Parameter oder negatives Forward-Verhalten.

Pflichtoutput: `release_decision.json` und `release_decision.md`.

## Versionierungsplan

- v0.2.1: CI / Packaging GO.
- v0.3.0: Real Data + Export Contract.
- v0.4.0: AMLR-X Parity Release.
- v0.5.0: Multi-Symbol Walk-forward.
- v0.6.0: Optimizer / Robustness.
- v0.7.0: Strategy Expansion.
- v0.8.0: Forward Shadow Logger.
- v0.9.0: Release Candidate.
- v1.0.0: Release-GO Framework.

## Pflichtkommandos

```bash
python -m compileall -q src scripts
pytest -q
python scripts/make_sample_data.py --rows 3500 --out data/processed/sample_BTCUSDT_5m.csv
python scripts/run_no_future_leak_check.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml --warmup-bars 250
python scripts/run_walk_forward.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml
python scripts/run_optimizer.py --data data/processed/sample_BTCUSDT_5m.csv --strategy amlrx --config configs/amlrx_v0_1.yaml
```

Bis v1.0.0 zusätzlich bereitstellen: `run_data_quality.py`, `run_export_schema_check.py`, `run_multi_symbol_walk_forward.py`, `run_release_gate.py`.

## GitHub-Arbeitsweise

Branch pro Version erstellen, Patch committen, Tests dokumentieren, PR öffnen, CI prüfen und nur mergen, wenn Tests grün sind, Scope sauber ist, keine fremden Änderungen überschrieben werden und keine kritischen Blocker offen sind.

Commit-Stil: `Harden CI packaging to v0.2.1`, `Add real data and export contract gates`, `Add AMLR-X parity release gate`, `Add multi-symbol walk-forward runner`, `Add v1.0.0 release decision framework`.

Nach jedem erfolgreichen Merge: `git pull origin main`, Versionsnummer und CHANGELOG aktualisieren, annotiertes Tag erstellen und pushen. Release-Workflow für Tag -> GitHub Release vorbereiten. Keine direkten Commits auf `main` ohne PR, außer dokumentierter Hotfix.

## Akzeptanzkriterien v1.0.0

```text
[ ] CI grün
[ ] compileall grün
[ ] pytest grün
[ ] Data Quality Gate vorhanden
[ ] Pine Export Schema Gate vorhanden
[ ] Pine-vs-Python Parity Gate vorhanden
[ ] Prefix-Stability / Future-Leak Gate vorhanden
[ ] MTF Confirmed-Bar Gate vorhanden
[ ] Walk-forward Engine vorhanden
[ ] Multi-Symbol Runner vorhanden
[ ] Robustness Metrics vorhanden
[ ] Release Decision Engine vorhanden
[ ] Reports als JSON und Markdown vorhanden
[ ] README vollständig
[ ] CHANGELOG vollständig
[ ] AGENTS.md vollständig
[ ] Beispiel-Workflow dokumentiert
```

## Abschlussformat je Version

```text
Version:
Branch:
Commit:
PR:
Merge Status:
Tests:
Changed Files:
New Commands:
Known Limitations:
Next Version:
Decision:
```

Wenn ein Gate nicht bestanden ist, lautet die Entscheidung `HOLD` oder `NO-GO`, nicht `GO`.
