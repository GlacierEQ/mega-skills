"""Behavioral tests for the omero-integration package.

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

def test_validator_fails_closed_without_config():
    # Unconfigured environment contract: the validator must refuse without
    # contacting a server or logging credential values.
    result = run_cli(["scripts/validate_config.py", "--json"])
    data = json.loads(result.stderr)
    assert result.returncode == 2
    assert data["server_contacted"] is False
    assert data["credential_values_included"] is False
    assert data["status"] == "invalid"
