"""Behavioral tests for the relsa-severity-assessment package.

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


def test_documented_scoring_run():
    with tempfile.TemporaryDirectory() as td:
        out_csv = Path(td) / "scores.csv"
        ref = Path(td) / "reference.json"
        result = run_cli([
            "scripts/relsa_score.py", "assets/example_cohort.csv",
            "--variables", "weight,temp,score,il6",
            "--normalize", "weight,temp,il6",
            "--turned", "il6",
            "--score-scale", "score=8",
            "--baseline-time", "-1",
            "--reference-group", "condition=endpoint",
            "--save-reference", str(ref),
            "--out", str(out_csv),
        ])
        assert result.returncode == 0
        assert "reference model: assets/example_cohort.csv [condition=endpoint]" in result.stderr
        assert "animals=2" in result.stderr
        scores = out_csv.read_text(encoding="utf-8").strip().splitlines()
        assert len(scores) >= 2
        model = json.loads(ref.read_text(encoding="utf-8"))
        assert model
