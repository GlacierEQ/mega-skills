"""Behavioral tests for the deeptools package.

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

def test_workflow_catalogue_lists_chipseq():
    result = run_cli(["scripts/workflow_generator.py", "--list"])
    assert result.returncode == 0
    assert "chipseq_qc" in result.stdout
    assert "ChIP-seq Quality Control" in result.stdout
    assert "chipseq_analysis" in result.stdout
