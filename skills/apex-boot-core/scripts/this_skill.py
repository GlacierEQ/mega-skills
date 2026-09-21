#!/usr/bin/env python3
"""APEX Boot Core v2 — compatibility entrypoint.

This file intentionally delegates to the same v2 implementation as run.py and
skill.py so no legacy path can bypass Operator semantic binding or enrichment
transition semantics.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from boot_watchdog import main

if __name__ == "__main__":
    sys.exit(main())
