from __future__ import annotations

from enum import Enum


class SignalState(str, Enum):
    NEUTRAL = "Neutral"
    BUILD = "Build"
    ARMED_LONG = "Armed Long"
    ARMED_SHORT = "Armed Short"
    ACTIVE_LONG = "Active Long"
    ACTIVE_SHORT = "Active Short"
    COOLDOWN = "Cooldown"
