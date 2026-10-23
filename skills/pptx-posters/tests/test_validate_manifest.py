"""Behavioral tests for the pptx-posters package.

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

def test_validator_forbids_placeholder_content():
    result = run_cli(["scripts/validate_manifest.py", "assets/poster_manifest_template.json"])
    assert result.returncode == 2
    assert "placeholder content is forbidden" in result.stderr
    assert "$.document.id" in result.stderr
