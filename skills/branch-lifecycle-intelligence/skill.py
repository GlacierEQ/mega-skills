#!/usr/bin/env python3
"""Thin dispatcher for branch-lifecycle-intelligence."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts" / "branch_lifecycle.py"

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: branch-lifecycle-intelligence <plan|validate> [args...]")
        return 1
    sys.argv = [str(SCRIPT), *sys.argv[1:]]
    runpy.run_path(str(SCRIPT), run_name="__main__")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
