"""Behavioral tests for the glycoengineering package.

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

def test_builtin_demo_finds_sequons():
    result = run_cli(["scripts/glycoengineering_tools.py"])
    assert result.returncode == 0
    assert "'motif': 'NNS'" in result.stdout
    assert "'sequon_type': 'NXS'" in result.stdout
    assert "st_fraction" in result.stdout
