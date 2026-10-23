"""Behavioral tests for the matlab package.

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

def test_bundled_template_manifest_validates():
    result = run_cli(["scripts/validate_project_manifest.py", "--allow-missing-paths", "assets/project_manifest_template.json"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert "src/analyzeSignal.m" in data["entry_points"]
    assert data["executes"] is False
    assert data["allow_missing_paths"] is True
