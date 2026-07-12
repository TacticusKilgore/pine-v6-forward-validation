from __future__ import annotations

import argparse

import pandas as pd

from src.forward_logging.outcomes import resolve_signal_outcomes

parser = argparse.ArgumentParser()
parser.add_argument("--signals", required=True)
parser.add_argument("--candles", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

signals = pd.read_csv(args.signals)
candles = pd.read_csv(args.candles)
resolve_signal_outcomes(signals, candles).to_csv(args.out, index=False)
