"""Behavioral tests for the lab-hardware-cad package.

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

def test_standards_check_reports_verdicts():
    result = run_cli(["scripts/check.py", "standards"])
    assert result.returncode == 0
    assert "cage-system-30mm" in result.stdout
    assert "cuvette-standard-10mm" in result.stdout
    assert "UNVERIFIED" in result.stdout
