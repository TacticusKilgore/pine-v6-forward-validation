# Pine Export Evidence Reporting

## Purpose

Pine export evidence reporting verifies that declared TradingView diagnostic CSV exports are present and contain the minimum schema needed for parity validation.

This does not replace Pine-vs-Python parity. It is an upstream evidence gate that confirms the declared exports are usable.

## Required columns

Every diagnostic export must include:

```text
timestamp
EXP_longSignal
EXP_shortSignal
```

Recommended diagnostic columns:

```text
EXP_state
EXP_score
```

Strategy-specific exports may include additional fields such as levels, stop prices, score components, state-machine flags and failure-risk fields.

## Run without local files

This validates declared export coverage from the manifest only:

```bash
python scripts/run_pine_export_evidence.py \
  --manifest configs/real_validation_inputs.example.yaml \
  --json-out reports/parity/pine_export_evidence_example.json \
  --md-out reports/parity/pine_export_evidence_example.md
```

Missing files are treated as `DECLARED` rather than `ERROR` unless file existence is explicitly required.

## Run with real local files

Use a local manifest and require actual files:

```bash
python scripts/run_pine_export_evidence.py \
  --manifest configs/real_validation_inputs.local.yaml \
  --require-existing-files \
  --json-out reports/parity/pine_export_evidence_local.json \
  --md-out reports/parity/pine_export_evidence_local.md
```

## Severity levels

| Severity | Meaning |
|---|---|
| OK | File exists and required/recommended schema is present. |
| DECLARED | Path is declared but file existence was not required. |
| WARNING | Required schema is present but recommended diagnostics are missing. |
| ERROR | File is missing, unreadable or required columns are absent. |

## Release rule

A passing export evidence report is not a final release `GO`. It only verifies that export files are declared and schema-usable. The project remains `HOLD` until parity reports confirm zero critical mismatches against Python mirror outputs.
