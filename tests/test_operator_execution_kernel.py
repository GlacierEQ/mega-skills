import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "skills" / "casey-operator-execution-kernel" / "skill.py"


def run_kernel(operation, payload):
    if operation in {"mission_select", "dispatch_gate"} and "context_hydration" not in payload:
        payload = dict(payload)
        payload["context_hydration"] = {
            "status": "PARTIAL",
            "attempted": True,
            "before_interpretation": True,
            "silent_prompt_only_fallback_forbidden": True,
            "sources": ["test-context"],
            "failures": [],
            "unknowns": ["full history coverage not asserted in fixture"],
        }
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


    def test_context_gate_rejects_missing_turn_hydration(self):
        result = run_kernel("context_gate", {})
        self.assertFalse(result["valid"])
        self.assertIn("turn_context_hydration_missing", result["reasons"])

    def test_context_gate_accepts_partial_hydration_and_continues(self):
        result = run_kernel("context_gate", {
            "context_hydration": {
                "status": "PARTIAL",
                "attempted": True,
                "before_interpretation": True,
                "silent_prompt_only_fallback_forbidden": True,
                "sources": ["conversation-history", "repository-state"],
                "failures": [],
                "unknowns": ["one connector unavailable"],
            }
        })
        self.assertTrue(result["valid"])
        self.assertTrue(result["mission_continues_if_partial_or_unavailable"])

    def test_dispatch_rejects_prompt_only_cognition(self):
        result = run_kernel("dispatch_gate", {
            "context_hydration": {
                "status": "PARTIAL",
                "attempted": False,
                "before_interpretation": False,
                "silent_prompt_only_fallback_forbidden": False,
                "sources": [],
                "failures": [],
                "unknowns": [],
            },
            "scope": {"mode": "specialized", "lane": "engineering"},
            "continuation_hydrated": True,
            "candidates": [{
                "id": "candidate", "lane": "engineering",
                "source_state_hydrated": True,
                "authorized": True, "executable": True, "substantive": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertFalse(result["dispatch_allowed"])
        self.assertIn("turn_context_retrieval_not_attempted", result["hydration_reasons"])
        self.assertIn("turn_context_not_hydrated_before_interpretation", result["hydration_reasons"])

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
        self.assertFalse(result["dispatch_allowed"])
        self.assertIn("operator_objective_graph_not_hydrated", result["hydration_reasons"])
        self.assertIn("cross_estate_front_comparison_missing", result["hydration_reasons"])

    def test_broad_estate_rejects_recent_artifact_lane_capture(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "estate"},
            "objective_graph_hydrated": True,
            "fronts_considered": [{"lane": "nex"}, {"lane": "engineering"}],
            "candidates": [
                {
                    "id": "recent-nex-matrix", "lane": "nex",
                    "source_state_hydrated": True,
                    "authorized": True, "executable": True, "substantive": True,
                    "result_kind": "matrix", "selection_basis": ["recent_context"],
                    "operator_impact": 1.0,
                },
                {
                    "id": "runtime-capability", "lane": "engineering",
                    "source_state_hydrated": True,
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
            "objective_graph_hydrated": True,
            "fronts_considered": [{"lane": "engineering"}, {"lane": "job"}],
            "candidates": [{
                "id": "ci-watch", "lane": "engineering",
                "source_state_hydrated": True,
                "authorized": True, "executable": True, "substantive": True,
                "support_only": True, "operator_impact": 1.0,
            }],
        })
        self.assertFalse(result["dispatch_allowed"])
        self.assertEqual(
            result["status"],
            "mission_hydration_or_substantive_candidate_required",
        )

    def test_specialized_worker_stays_in_lane(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "specialized", "lane": "supabase"},
            "continuation_hydrated": True,
            "candidates": [
                {"id": "nex-real", "lane": "nex", "source_state_hydrated": True,
                 "authorized": True, "executable": True, "substantive": True,
                 "operator_impact": 1.0},
                {"id": "supabase-runtime", "lane": "supabase",
                 "source_state_hydrated": True, "authorized": True,
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

    def test_verified_boolean_without_receipt_cannot_finalize(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": True,
            "verified": True,
            "support_only": False,
            "artifact_only": False,
            "authorized_executable_action_exists": False,
        })
        self.assertFalse(result["can_finalize"])
        self.assertIn("verification_reference_missing", result["reasons"])

    def test_completion_gate_allows_verified_real_delta_with_receipt(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": True,
            "verified": True,
            "verification_refs": ["readback-receipt-123"],
            "artifact_only": False,
            "support_only": False,
            "authorized_executable_action_exists": False,
        })
        self.assertTrue(result["can_finalize"])
        self.assertEqual(result["finalization_kind"], "verified_mission_delta")
        self.assertFalse(result["continue_required"])

    def test_hard_boundary_can_finalize_without_false_success(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": False,
            "verified": False,
            "hard_external_boundary": True,
            "authorized_executable_action_exists": False,
        })
        self.assertTrue(result["can_finalize"])
        self.assertEqual(result["finalization_kind"], "hard_boundary")
        self.assertFalse(result["continue_required"])

    def test_retirement_gate_keeps_branch_active_while_unique_state_remains(self):
        result = run_kernel("retirement_gate", {
            "unique_sources_remaining": 1,
            "unique_events_remaining": 2,
            "unique_edges_remaining": 0,
            "unique_contradictions_remaining": 1,
            "unique_provenance_remaining": 0,
            "unique_unresolved_dependencies_remaining": 0,
            "unique_receipts_remaining": 0,
            "merged_target_readback_verified": True,
            "preserves_lineage": True,
        })
        self.assertFalse(result["can_retire"])
        self.assertEqual(result["branch_state"], "ACTIVE_IN_MESH")
        self.assertEqual(result["action"], "merge_continue")
        self.assertEqual(result["total_unique_remaining"], 4)

    def test_retirement_gate_allows_only_drained_lineage_preserved_branch(self):
        result = run_kernel("retirement_gate", {
            "unique_sources_remaining": 0,
            "unique_events_remaining": 0,
            "unique_edges_remaining": 0,
            "unique_contradictions_remaining": 0,
            "unique_provenance_remaining": 0,
            "unique_unresolved_dependencies_remaining": 0,
            "unique_receipts_remaining": 0,
            "merged_target_readback_verified": True,
            "preserves_lineage": True,
        })
        self.assertTrue(result["can_retire"])
        self.assertEqual(result["branch_state"], "RETIRED_DERIVATIVE")
        self.assertEqual(result["action"], "retire_with_lineage")

    def test_mission_select_rejects_replacement_that_would_drop_unique_state(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "specialized", "lane": "case"},
            "continuation_hydrated": True,
            "candidates": [
                {
                    "id": "swap-tree", "lane": "case",
                    "source_state_hydrated": True,
                    "authorized": True, "executable": True, "substantive": True,
                    "replace_existing": True,
                    "retirement_check": {
                        "unique_sources_remaining": 1,
                        "merged_target_readback_verified": True,
                        "preserves_lineage": True,
                    },
                    "operator_impact": 1.0,
                },
                {
                    "id": "grow-tree", "lane": "case",
                    "source_state_hydrated": True,
                    "authorized": True, "executable": True, "substantive": True,
                    "merge_extends_existing_state": True,
                    "continuation_valid": True,
                    "operator_impact": 0.8,
                },
            ],
        })
        self.assertEqual(result["selected"]["id"], "grow-tree")
        rejected = {item["id"]: item["reasons"] for item in result["rejected"]}
        self.assertIn("replacement_would_discard_unique_state", rejected["swap-tree"])

    def test_completion_gate_blocks_unproven_replacement(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": True,
            "verified": True,
            "verification_refs": ["receipt-1"],
            "artifact_only": False,
            "support_only": False,
            "authorized_executable_action_exists": False,
            "replacement_attempted": True,
            "retirement_check": {
                "unique_events_remaining": 1,
                "merged_target_readback_verified": True,
                "preserves_lineage": True,
            },
        })
        self.assertFalse(result["can_finalize"])
        self.assertIn("replacement_would_discard_unique_state", result["reasons"])
        self.assertEqual(result["retirement"]["branch_state"], "ACTIVE_IN_MESH")


if __name__ == "__main__":
    unittest.main()
