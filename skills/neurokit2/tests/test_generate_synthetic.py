"""Behavioral tests for the neurokit2 package.

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


def test_synthetic_fixture_generation():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "synth.csv"
        result = run_cli(["scripts/generate_synthetic.py", "--root", td, "--output", str(out), "--duration", "10"])
        data = json.loads(result.stdout)
        assert result.returncode == 0
        assert data["artifact"] == "synthetic_biosignal_fixture"
        assert "ecg" in data["columns"]
        assert data["duration_s"] == 10.0
        rows = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) > 100
