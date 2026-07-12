from __future__ import annotations

import argparse

from src.forward_logging.drive_sync import sync_directory

parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", required=True)
parser.add_argument("--parent-folder-id", required=True)
args = parser.parse_args()
print(sync_directory(args.run_dir, args.parent_folder_id))
