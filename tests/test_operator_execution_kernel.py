import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "skills" / "casey-operator-execution-kernel" / "skill.py"


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


class OperatorExecutionKernelTests(unittest.TestCase):
    def test_kernel_entrypoint_exists(self):
        self.assertTrue(KERNEL.is_file())

    def test_broad_estate_rejects_recent_artifact_lane_capture(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "estate"},
            "candidates": [
                {
                    "id": "recent-nex-matrix", "lane": "nex",
                    "authorized": True, "executable": True, "substantive": True,
                    "artifact_only": True, "recency_only": True,
                    "operator_impact": 1.0,
                },
                {
                    "id": "runtime-capability", "lane": "engineering",
                    "authorized": True, "executable": True, "substantive": True,
                    "continuation_valid": True, "operator_impact": 0.9,
                    "blocked_downstream": 0.8, "capability_gain": 1.0,
                    "compounding_value": 1.0, "execution_readiness": 0.9,
                    "prior_investment": 0.9,
                },
            ],
        })
        self.assertEqual(result["selected"]["id"], "runtime-capability")
        rejected = {item["id"]: item["reasons"] for item in result["rejected"]}
        self.assertIn("artifact_only", rejected["recent-nex-matrix"])
        self.assertIn("recency_only", rejected["recent-nex-matrix"])

    def test_support_only_candidate_cannot_dispatch(self):
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "estate"},
            "candidates": [{
                "id": "ci-watch", "lane": "engineering",
                "authorized": True, "executable": True, "substantive": True,
                "support_only": True, "operator_impact": 1.0,
            }],
        })
        self.assertFalse(result["dispatch_allowed"])
        self.assertEqual(result["status"], "no_substantive_dispatch_candidate")

    def test_specialized_worker_stays_in_lane(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "specialized", "lane": "supabase"},
            "candidates": [
                {"id": "nex-real", "lane": "nex", "authorized": True,
                 "executable": True, "substantive": True, "operator_impact": 1.0},
                {"id": "supabase-runtime", "lane": "supabase", "authorized": True,
                 "executable": True, "substantive": True, "continuation_valid": True,
                 "operator_impact": 0.8, "capability_gain": 0.9,
                 "execution_readiness": 1.0},
            ],
        })
        self.assertEqual(result["selected"]["id"], "supabase-runtime")
        self.assertIn("outside_specialized_lane", result["rejected"][0]["reasons"])

    def test_completion_gate_rejects_artifact_only_progress(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": False,
            "verified": True,
            "artifact_only": True,
            "support_only": True,
            "authorized_executable_action_exists": True,
        })
        self.assertFalse(result["can_finalize"])
        self.assertTrue(result["continue_required"])
        self.assertIn("artifact_only_output_is_not_mission_completion", result["reasons"])
        self.assertIn("authorized_executable_action_still_exists", result["reasons"])

    def test_completion_gate_allows_only_verified_real_delta_with_no_work_left(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": True,
            "verified": True,
            "artifact_only": False,
            "support_only": False,
            "authorized_executable_action_exists": False,
        })
        self.assertTrue(result["can_finalize"])
        self.assertFalse(result["continue_required"])


if __name__ == "__main__":
    unittest.main()
