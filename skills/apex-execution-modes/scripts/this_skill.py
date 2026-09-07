#!/usr/bin/env python3
"""Compatibility entrypoint that delegates to the canonical APEX execution contract."""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from skill import main

if __name__ == "__main__":
    raise SystemExit(main())
