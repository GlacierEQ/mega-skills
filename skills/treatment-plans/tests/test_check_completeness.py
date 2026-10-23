"""Behavioral tests for the treatment-plans package.

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

def test_completeness_check_names_withheld_determinations():
    result = run_cli(["scripts/check_completeness.py", "assets"])
    data = json.loads(result.stdout)
    assert result.returncode == 1
    assert data["check"] == "documentation_completeness"
    assert "clinical_correctness" in data["determinations_not_made"]
