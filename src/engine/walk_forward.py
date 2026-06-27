from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def chronological_windows(total_bars: int, train_bars: int, test_bars: int, step_bars: int) -> Iterator[WalkForwardWindow]:
    start = 0
    while start + train_bars + test_bars <= total_bars:
        yield WalkForwardWindow(start, start + train_bars, start + train_bars, start + train_bars + test_bars)
        start += step_bars
