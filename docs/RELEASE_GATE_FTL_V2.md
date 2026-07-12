# FTL_V2 Release Gate

| Gate | Status | Reason |
|---|---:|---|
| Event schema | GO | FTL_V2 schema and strict Python validation implemented. |
| Deterministic IDs and dedupe | GO | SHA-256 IDs and SQLite claim store implemented. |
| Raw append-only store | GO | JSONL store implemented. |
| Normalized event output | GO | Flattened CSV output implemented. |
| Outcome resolver | GO | Future-only 1/3/5/10-bar, MFE/MAE and touch classification implemented. |
| Pine transport harness | SOFT-GO | Compile-ready design supplied; TradingView compile and webhook smoke test remain external. |
| Cloud ingress | SOFT-GO | Flask/PubSub implementation supplied; GCP deployment not executed. |
| Drive synchronization | SOFT-GO | Drive API implementation supplied; runtime credentials remain external. |
| Real forward evidence | HOLD | Requires live TradingView events and validated Bybit data. |
| Production release | HOLD | External evidence and deployed infrastructure are required. |

## Decision

```text
HOLD
```

The implementation framework is complete enough for a controlled deployment. Final GO is prohibited until real TradingView, Bybit and forward-reconciliation evidence passes the existing repository gates.
