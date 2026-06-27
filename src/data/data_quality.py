from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import pandas as pd

from src.data.schema import normalize_ohlcv_frame, validate_ohlcv_frame


@dataclass(frozen=True)
class DataQualityGateReport:
    symbol: str
    timeframe: str
    rows: int
    start: str | None
    end: str | None
    missing_candles: int
    duplicate_timestamps: int
    non_positive_prices: int
    negative_volume: int
    inferred_timeframe: str | None
    passed: bool
    gaps: list[dict]
    missing_values: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


def write_data_quality_report(report: DataQualityGateReport, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path
