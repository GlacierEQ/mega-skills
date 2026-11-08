#!/usr/bin/env python3
"""APEX Boot Core v2 — CLI entry point (scripts/run.py)."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from boot_watchdog import main

if __name__ == "__main__":
    sys.exit(main())
