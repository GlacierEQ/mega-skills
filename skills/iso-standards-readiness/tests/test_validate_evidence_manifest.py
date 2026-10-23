"""Behavioral tests for the iso-standards-readiness package.

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

def test_validator_reports_template_gaps():
    result = run_cli(["scripts/validate_evidence_manifest.py", "assets/templates/evidence-manifest-template.json"])
    data = json.loads(result.stdout)
    assert result.returncode == 1
    assert data["basis_date"] == "2026-10-01"
    assert len(data["findings"]) >= 1
    assert data["findings"][0]["code"] == "APPROVAL_PENDING"
