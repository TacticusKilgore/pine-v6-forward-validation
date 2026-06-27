from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalState(str, Enum):
    NEUTRAL = "Neutral"
    BUILD = "Build"
    ARMED_LONG = "Armed Long"
    ARMED_SHORT = "Armed Short"
    ACTIVE_LONG = "Active Long"
    ACTIVE_SHORT = "Active Short"
    FAILED = "Failed"
    COOLDOWN = "Cooldown"


@dataclass
class CooldownState:
    bars_remaining: int = 0

    @property
    def active(self) -> bool:
        return self.bars_remaining > 0

    def tick(self) -> None:
        if self.bars_remaining > 0:
            self.bars_remaining -= 1

    def start(self, bars: int) -> None:
        self.bars_remaining = max(0, int(bars))
