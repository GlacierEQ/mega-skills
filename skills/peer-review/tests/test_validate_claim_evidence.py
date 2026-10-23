"""Behavioral tests for the peer-review package.

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

def test_bundled_matrix_counts_claims():
    result = run_cli(["scripts/validate_claim_evidence.py", "assets/claim_evidence_matrix_template.csv"])
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert data["claim_count"] == 3
    assert "CLAIM-SYN-002" in data["claim_ids_requiring_resolution"]
