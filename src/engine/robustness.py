from __future__ import annotations

from itertools import product


def build_parameter_grid(base: dict, perturbations: dict[str, list]) -> list[dict]:
    keys = list(perturbations)
    return [base | dict(zip(keys, vals, strict=True)) for vals in product(*(perturbations[k] for k in keys))]
