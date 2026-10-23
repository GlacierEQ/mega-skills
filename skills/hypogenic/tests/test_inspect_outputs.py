"""Behavioral tests for the hypogenic package.

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

def test_bundled_result_example_inspects():
    result = run_cli(["scripts/inspect_outputs.py", "results", "--input", "assets/result.example.json"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert len(data["file_sha256"]) == 64
    assert data["file_sha256"] != "0" * 64
    assert data["candidate_metrics_are_scientific_validation"] is False
