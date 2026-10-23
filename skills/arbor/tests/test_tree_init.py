"""Behavioral tests for the arbor package.

Each test executes the package's own implementation -- the same CLI the
skill documents for its users -- and asserts on the substantive output
produced. Recorded during the 2026-10-23 readiness raise-up: verification
exists only where the implementation actually ran in this environment and
produced its documented verdict.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(args, cwd=None):
    return subprocess.run(
        [sys.executable] + args,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )

import os
import tempfile


def test_init_creates_run_state():
    with tempfile.TemporaryDirectory() as td:
        result = run_cli(["scripts/tree.py", "--run-dir", td, "init", "--objective", "raise test coverage", "--dev-eval", "dev.json", "--test-eval", "test.json"])
        assert result.returncode == 0
        assert "Initialized Arbor run" in result.stdout
        names = os.listdir(Path(td) / ".arbor")
        assert len(names) >= 1
