from __future__ import annotations

from src.strategies.amlrx import AMLRXStrategy
from src.strategies.iax import IAXStrategy
from src.strategies.ivsf import IVSFStrategy
from src.strategies.elc import ELCStrategy

STRATEGIES = {
    "amlrx": AMLRXStrategy,
    "iax": IAXStrategy,
    "ivsf": IVSFStrategy,
    "elc": ELCStrategy,
}


def build_strategy(name: str, config: dict):
    key = name.lower().strip()
    if key not in STRATEGIES:
        raise ValueError(f"Unknown strategy '{name}'. Available: {sorted(STRATEGIES)}")
    return STRATEGIES[key].from_config(config)
