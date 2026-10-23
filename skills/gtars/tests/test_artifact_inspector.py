"""Behavioral tests for the gtars package.

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

def test_inspector_reports_artifact_without_executing():
    result = run_cli(["scripts/artifact_inspector.py", "--artifact", "scripts/_common.py"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert len(data["artifacts"]) == 1
    assert data["artifacts"][0]["executed"] is False
    assert data["artifacts"][0]["kind"] == "data-or-metadata"
