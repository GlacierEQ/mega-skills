#!/usr/bin/env python3
"""Launch the repo Unified Memory MCP server."""

from __future__ import annotations

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parents[3] / "scripts" / "unified_memory_mcp.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
