#!/usr/bin/env python3
"""Compatibility runner for desktop-commander-overview."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
namespace = runpy.run_path(str(ROOT / "skill.py"))
raise SystemExit(namespace["main"]())
