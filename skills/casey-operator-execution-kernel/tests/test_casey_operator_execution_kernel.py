#!/usr/bin/env python3
"""Behavioral tests for casey-operator-execution-kernel."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KERNEL = Path(__file__).resolve().parents[1] / "skill.py"


def run_kernel(operation, payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(payload, handle)
        input_path = handle.name
    try:
        proc = subprocess.run(
            [sys.executable, str(KERNEL), operation, "--input", input_path],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
    finally:
        Path(input_path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    return json.loads(proc.stdout)


class TestCaseyOperatorExecutionKernel(unittest.TestCase):
    def test_kernel_entrypoint(self):
        self.assertTrue(KERNEL.is_file())

    def test_estate_dispatch_requires_real_objective_graph_hydration(self):
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "estate"},
            "candidates": [{
                "id": "easy-one", "lane": "engineering",
                "source_state_hydrated": True,
                "authorized": True, "executable": True, "substantive": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertFalse(result.get("dispatch_allowed"))
        reasons = result.get("hydration_reasons", [])
        self.assertTrue("operator_objective_graph_not_hydrated" in reasons)
        self.assertTrue("cross_estate_front_comparison_missing" in reasons)

    def test_purpose_operation(self):
        result = run_kernel("purpose", {})
        self.assertTrue("purpose" in result or "skill" in result or "operation" in result)


if __name__ == "__main__":
    unittest.main()
