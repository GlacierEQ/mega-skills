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

    def test_estate_dispatch_records_context_debt_without_mission_stop(self):
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "estate"},
            "candidates": [{
                "id": "easy-one", "lane": "engineering",
                "source_state_hydrated": False,
                "authorized": True, "executable": True, "substantive": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertTrue(result.get("dispatch_allowed"))
        self.assertEqual(result.get("status"), "dispatch_allowed_context_recovery_in_flight")
        self.assertEqual(result.get("context_state"), "recovery_pending")
        self.assertFalse(result.get("context_mission_stop_authority"))
        self.assertTrue(result.get("context_recovery_debt", {}).get("open"))
        reasons = result.get("hydration_reasons", [])
        self.assertIn("operator_objective_graph_not_hydrated", reasons)
        self.assertIn("cross_estate_front_comparison_missing", reasons)

    def test_real_authority_constraint_still_rejects_candidate(self):
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "specialized", "lane": "engineering"},
            "context_hydration": {
                "status": "UNAVAILABLE",
                "attempted": True,
                "before_interpretation": True,
                "silent_prompt_only_fallback_forbidden": True,
                "sources": [],
                "failures": ["provider unavailable"],
                "unknowns": ["prior state incomplete"],
            },
            "continuation_hydrated": False,
            "candidates": [{
                "id": "unauthorized", "lane": "engineering",
                "source_state_hydrated": False,
                "authorized": False, "executable": True, "substantive": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertFalse(result.get("dispatch_allowed"))
        rejected = result.get("rejected", [])
        self.assertTrue(any("not_authorized" in row.get("reasons", []) for row in rejected))

    def test_purpose_operation(self):
        result = run_kernel("purpose", {})
        self.assertTrue("purpose" in result or "skill" in result or "operation" in result)


if __name__ == "__main__":
    unittest.main()
