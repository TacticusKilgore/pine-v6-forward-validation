from __future__ import annotations

from itertools import product


def grid_search(param_grid: dict[str, list], objective):
    keys = list(param_grid)
    rows = []
    for vals in product(*(param_grid[k] for k in keys)):
        params = dict(zip(keys, vals, strict=True))
        rows.append({"params": params, "score": float(objective(params))})
    return sorted(rows, key=lambda r: r["score"], reverse=True)
