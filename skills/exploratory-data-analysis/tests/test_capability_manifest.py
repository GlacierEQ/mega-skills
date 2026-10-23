"""Behavioral tests for the exploratory-data-analysis package.

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

def test_manifest_lists_automated_capabilities():
    result = run_cli(["scripts/capability_manifest.py", "list"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert len(data["automated"]) >= 3
    formats = {entry["format"] for entry in data["automated"]}
    assert "CSV" in formats
