"""Behavioral tests for the onekgpd package.

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

def test_superpopulations_from_bundled_data():
    result = run_cli(["scripts/onekgpd_meta.py", "list-superpopulations"])
    assert result.returncode == 0
    assert "5 superpopulations" in result.stdout
    assert "AFR" in result.stdout and "n=893" in result.stdout
    assert "EUR" in result.stdout and "n=633" in result.stdout
