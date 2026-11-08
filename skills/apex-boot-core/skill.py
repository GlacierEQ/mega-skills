#!/usr/bin/env python3
"""APEX Boot Core v2 — CLI entry point and skill.py wrapper."""

import json
import sys
from pathlib import Path

# Ensure scripts dir is importable
HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "scripts"
sys.path.insert(0, str(SCRIPTS))

from boot_watchdog import ApexBootCore, main


if __name__ == "__main__":
    sys.exit(main())
