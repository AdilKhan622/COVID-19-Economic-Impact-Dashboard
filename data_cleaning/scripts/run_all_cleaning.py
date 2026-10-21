#!/usr/bin/env python3
"""Run the complete cleaning pipeline in a reproducible order."""

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "clean_world_bank_metadata.py",
    "clean_oxcgrt.py",
    "clean_google_mobility.py",
    "merge_cleaned_datasets.py",
    "validate_cleaned_data.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n=== Running {script} ===", flush=True)
        subprocess.run([sys.executable, str(SCRIPT_DIR / script)], check=True)


if __name__ == "__main__":
    main()
