from __future__ import annotations

import argparse

from src.forward_logging.worker import process_spool

parser = argparse.ArgumentParser()
parser.add_argument("--spool", required=True)
parser.add_argument("--run-dir", required=True)
args = parser.parse_args()
print(process_spool(args.spool, args.run_dir))
