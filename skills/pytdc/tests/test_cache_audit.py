"""Behavioral tests for the pytdc package.

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


def test_empty_cache_audits_clean():
    with tempfile.TemporaryDirectory() as td:
        Path(td, "cache").mkdir()
        result = run_cli([str(ROOT / "scripts" / "cache_audit.py"), "--cache-dir", "cache"], cwd=td)
        data = json.loads(result.stdout)
        assert result.returncode == 0
        assert data["file_count"] == 0
        assert data["errors"] == []
        assert data["download_performed"] is False
