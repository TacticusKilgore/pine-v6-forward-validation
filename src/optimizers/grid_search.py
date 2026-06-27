from __future__ import annotations

from itertools import product
from typing import Any, Callable
import pandas as pd


def grid_search(param_grid: dict[str, list[Any]], objective: Callable[[dict[str, Any]], dict[str, Any]]) -> pd.DataFrame:
    keys = list(param_grid.keys())
    rows = []
    for values in product(*(param_grid[k] for k in keys)):
        params = dict(zip(keys, values))
        result = objective(params)
        rows.append({**params, **result})
    return pd.DataFrame(rows)
