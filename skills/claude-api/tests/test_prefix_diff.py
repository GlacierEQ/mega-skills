"""Behavioral tests for the claude-api package.

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

def test_scan_reports_leads_over_package_docs():
    result = run_cli(["shared/preserved-thinking-migration/prefix_diff.py", "--scan", "shared"])
    assert result.returncode == 0
    assert "file(s) read under shared" in result.stdout
    assert "LEADS" in result.stdout
