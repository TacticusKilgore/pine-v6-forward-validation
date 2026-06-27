from __future__ import annotations


def round_trip_cost_fraction(fee_bps: float = 5.5, slippage_bps: float = 2.0) -> float:
    return 2.0 * (fee_bps + slippage_bps) / 10_000.0
