# FTL_V2 Automated Forward Logging

## Scope

This package adds the missing real-time acquisition layer to `pine-v6-forward-validation` without changing the existing parity, walk-forward or release-gate engines.

## Runtime flow

```text
Pine alert()
-> Cloud Run ingress
-> Pub/Sub
-> worker
-> append-only JSONL
-> normalized CSV
-> outcome resolver
-> Google Drive sync
```

## Hard rules

- Confirmed-bar alerts only.
- UTC is canonical.
- Deterministic event IDs and deduplication.
- Raw events are append-only.
- Outcome candles must be strictly later than the signal bar.
- Blocked signals must be logged and resolved as shadow outcomes.
- Actual slippage is recorded only from a real or testnet fill source.

## Local smoke test

```bash
pip install -e ".[dev,forward]"
pytest -q
flask --app src.forward_logging.ingress run --port 8080
python scripts/process_forward_spool.py \
  --spool /tmp/forward_events.jsonl \
  --run-dir data/forward_runs/R01
```

## TradingView setup

1. Add `pine/forward_logger_transport_harness_v0_1_0.pine` to a 5-minute chart.
2. Create an alert using `Any alert() function call`.
3. Use the deployed `/webhook?token=<secret>` URL.
4. Verify `HEARTBEAT` and `SIGNAL_VALID` events in the raw JSONL log.
5. Recreate the alert after any code, input, symbol or timeframe change.

## Production deployment inputs still required

- GCP project ID.
- Pub/Sub topic and subscription.
- Cloud Run deployment permission.
- Google Drive service-account or ADC credentials.
- TradingView alert creation and webhook URL.
- Real Pine diagnostic exports and validated Bybit candles for final release evidence.
