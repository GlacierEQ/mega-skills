"""Behavioral tests for the get-available-resources package.

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

def test_detect_resources_reports_accelerators():
    result = run_cli(["scripts/detect_resources.py"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    counts = data["accelerators"]["candidate_counts"]
    assert {"cuda", "metal", "rocm"} <= set(counts)
    assert all(isinstance(value, int) and value >= 0 for value in counts.values())
