from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    fee_bps_per_side: float = 6.0
    slippage_bps_per_side: float = 2.0

    @property
    def round_trip_bps(self) -> float:
        return 2.0 * (self.fee_bps_per_side + self.slippage_bps_per_side)

    def apply_entry_long(self, price: float) -> float:
        return price * (1.0 + self.slippage_bps_per_side / 10_000.0)

    def apply_entry_short(self, price: float) -> float:
        return price * (1.0 - self.slippage_bps_per_side / 10_000.0)

    def net_return_fraction(self, gross_return_fraction: float) -> float:
        return gross_return_fraction - self.round_trip_bps / 10_000.0
