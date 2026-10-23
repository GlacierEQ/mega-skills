"""Behavioral tests for the 13c-metabolic-flux package.

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

def test_check_accepts_bundled_tca_model():
    result = run_cli(["scripts/mfa.py", "check", "--model", "assets/tca-model.json", "--data", "assets/tca-tracer.json"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert data["command"] == "check"
    assert data["model"] == "Published EMU TCA demonstration"
    digests = data["input_sha256"]
    assert len(digests) >= 2
    assert all(len(value) == 64 for value in digests.values())
