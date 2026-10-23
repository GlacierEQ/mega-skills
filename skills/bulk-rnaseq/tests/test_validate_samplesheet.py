"""Behavioral tests for the bulk-rnaseq package.

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


def test_documented_samplesheet_format_validates():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "r1.fastq.gz").write_bytes(b"")
        (base / "r2.fastq.gz").write_bytes(b"")
        sheet = base / "samplesheet.csv"
        sheet.write_text(
            "sample,fastq_1,fastq_2,strandedness\nS1,%s,%s,auto\n" % (base / "r1.fastq.gz", base / "r2.fastq.gz"),
            encoding="utf-8",
        )
        result = run_cli([str(ROOT / "scripts" / "validate_samplesheet.py"), "--samplesheet", str(sheet)], cwd=td)
        assert result.returncode == 0
        assert "PASSED: 0 errors" in result.stdout
        assert "1 unique sample(s)" in result.stdout
