"""Behavioral tests for the geniml package.

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

import tempfile


def test_minimal_bed_validates():
    with tempfile.TemporaryDirectory() as td:
        bed = Path(td) / "t.bed"
        bed.write_text("chr1\t100\t200\nchr1\t300\t450\n", encoding="utf-8")
        result = run_cli(["scripts/bed_validator.py", "--input", str(bed), "--assembly", "hg38"])
        data = json.loads(result.stdout)
        assert result.returncode == 0
        assert data["contract"]["assembly"] == "hg38"
        assert data["contract"]["coordinate_system"] == "0-based-half-open"
        assert data["errors"] == {}
