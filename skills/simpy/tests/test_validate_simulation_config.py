"""Behavioral tests for the simpy package.

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

QUEUE_CONFIG = {
    "analysis_mode": "terminating",
    "base_seed": 20260723,
    "horizon": 480.0,
    "max_entities": 10000,
    "max_events": 200000,
    "mean_interarrival": 4.0,
    "mean_service": 6.0,
    "queue_capacity": 20,
    "servers": 2,
    "warm_up": 0.0,
}


def test_documented_queue_config_validates():
    with tempfile.TemporaryDirectory() as td:
        cfg = Path(td) / "queue.json"
        cfg.write_text(json.dumps(QUEUE_CONFIG), encoding="utf-8")
        result = run_cli(["scripts/validate_simulation_config.py", "--schema", "queue", str(cfg)])
        data = json.loads(result.stdout)
        assert result.returncode == 0
        assert data["budgets"]["entities"] == 10000
        assert data["budgets"]["time"] == 480.0
