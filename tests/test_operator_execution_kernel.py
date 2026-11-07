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

    def test_dispatch_surfaces_prompt_only_hydration_debt_without_vetoing(self):
        """Un-hydrated turn context must be reported as debt, not as a veto.

        The kernel implements "enrichment, not permission": a degraded context
        cannot stop a mission, but it must never pass silently. This asserts
        both halves -- dispatch may proceed, and the debt is still on the record.
        """
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
        # The debt is recorded and remains open.
        self.assertIn("turn_context_retrieval_not_attempted", result["hydration_reasons"])
        self.assertIn("turn_context_not_hydrated_before_interpretation", result["hydration_reasons"])
        self.assertFalse(result["hydration_valid"])
        self.assertNotEqual(result["context_state"], "hydrated")
        self.assertTrue(result["context_recovery_debt"]["open"])
        self.assertFalse(result["context_recovery_debt"]["mission_stop"])
        # Hydration is enrichment, not permission: it does not veto dispatch.
        self.assertTrue(result["dispatch_allowed"])
        self.assertEqual(
            result["status"], "dispatch_allowed_context_recovery_in_flight"
        )
        self.assertEqual(result["context_transition_semantics"], "enrichment_not_permission")

    def test_operator_invariants_use_aspen_grove_epistemology(self):
        invariants = json.loads(
            (ROOT / "skills" / "casey-operator-execution-kernel" / "OPERATOR_INVARIANTS.json")
            .read_text(encoding="utf-8")
        )
        epistemology = invariants["epistemology"]
        self.assertEqual(epistemology["model"], "ASPEN_GROVE")
        self.assertEqual(epistemology["law"], "SHARED_ROOTS_INDEPENDENT_TRUNKS_COMPOSABLE_BRANCHES")
        self.assertTrue(epistemology["context_before_interpretation"])
        self.assertTrue(epistemology["domain_local_knowledge_by_default"])
        self.assertTrue(epistemology["cross_domain_composition_requires_typed_bridge"])
        self.assertTrue(epistemology["composition_must_not_merge_domain_identity"])
        self.assertTrue(epistemology["retrieval_is_not_proof"])
        self.assertTrue(epistemology["absence_of_retrieval_is_not_absence"])
        self.assertTrue(epistemology["evidence_and_execution_axes_separate"])
        self.assertTrue(epistemology["execution_is_not_verification"])

    def test_estate_dispatch_records_objective_graph_hydration_debt(self):
        """Estate scope must surface objective-graph debt without vetoing dispatch.

        Matches the kernel's "enrichment, not permission" law: the missing
        hydration is recorded as open debt, and dispatch is not blocked by it.
        """
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "estate"},
            "candidates": [{
                "id": "easy-one", "lane": "engineering",
                "source_state_hydrated": True,
                "authorized": True, "executable": True, "substantive": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertIn("operator_objective_graph_not_hydrated", result["hydration_reasons"])
        self.assertIn("cross_estate_front_comparison_missing", result["hydration_reasons"])
        self.assertFalse(result["hydration_valid"])
        self.assertTrue(result["context_recovery_debt"]["open"])
        self.assertFalse(result["context_recovery_debt"]["mission_stop"])
        self.assertTrue(result["dispatch_allowed"])

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
        # Rejection behaviour is unchanged: a support-only candidate is never
        # dispatchable, and the reason is recorded on the rejection entry.
        self.assertFalse(result["dispatch_allowed"])
        self.assertIsNone(result["selected"])
        self.assertEqual([r["id"] for r in result["rejected"]], ["ci-watch"])
        self.assertIn("support_only", result["rejected"][0]["reasons"])
        self.assertEqual(
            result["status"],
            "substantive_executable_candidate_required",
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

    def test_operator_requested_finished_artifact_is_dispatchable_without_invented_substantive_flag(self):
        """A direct Operator artifact request is the mission, not forbidden support work."""
        result = run_kernel("dispatch_gate", {
            "scope": {"mode": "specialized", "lane": "engineering"},
            "continuation_hydrated": True,
            "candidates": [{
                "id": "deliver-requested-functional-patch",
                "lane": "engineering",
                "source_state_hydrated": True,
                "authorized": True,
                "executable": True,
                "substantive": False,
                "support_only": True,
                "artifact_only": True,
                "requested_finished_deliverable": True,
                "explicit_operator_priority": True,
                "operator_impact": 1.0,
            }],
        })
        self.assertTrue(result["dispatch_allowed"], result["rejected"])
        self.assertEqual(result["selected"]["id"], "deliver-requested-functional-patch")

    def test_explicitly_requested_support_does_not_trigger_no_action_default(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "specialized", "lane": "engineering"},
            "continuation_hydrated": True,
            "candidates": [{
                "id": "operator-requests-support-task",
                "lane": "engineering",
                "authorized": True,
                "executable": True,
                "substantive": False,
                "support_only": True,
                "result_kind": "audit",
                "explicitly_requested_support": True,
            }],
        })
        self.assertTrue(result["dispatch_allowed"], result["rejected"])

    def test_requested_finished_deliverable_can_finalize_on_verified_receipt(self):
        result = run_kernel("completion_gate", {
            "mission_state_changed": True,
            "verified": True,
            "verification_refs": ["owner-provider-readback-1"],
            "support_only": True,
            "artifact_only": True,
            "requested_finished_deliverable": True,
            "authorized_executable_action_exists": False,
        })
        self.assertTrue(result["can_finalize"], result["reasons"])
        self.assertEqual(result["finalization_kind"], "verified_mission_delta")

    def test_unrequested_support_and_artifacts_still_cannot_replace_real_mission(self):
        result = run_kernel("mission_select", {
            "scope": {"mode": "specialized", "lane": "engineering"},
            "continuation_hydrated": True,
            "candidates": [{
                "id": "unrequested-admin-audit",
                "lane": "engineering",
                "authorized": True, "executable": True,
                "substantive": False,
                "support_only": True,
                "artifact_only": True,
                "result_kind": "audit",
            }],
        })
        self.assertFalse(result["dispatch_allowed"])



    def test_requested_read_only_outcome_can_complete_without_mutating_state(self):
        payload = {"mission_state_changed": False, "requested_finished_deliverable": True,
                   "requested_outcome_complete": True, "verified": True,
                   "verification_refs": ["reviewed-source"], "artifact_only": True,
                   "support_only": True, "authorized_executable_action_exists": False}
        result = run_kernel("completion_gate", payload)
        self.assertTrue(result["can_finalize"], result["reasons"])
        self.assertEqual(result["finalization_kind"], "verified_requested_outcome")
        for key, value in (("requested_outcome_complete", False), ("verified", False),
                           ("verification_refs", []), ("authorized_executable_action_exists", True),
                           ("requested_finished_deliverable", False), ("replacement_attempted", True)):
            with self.subTest(key=key):
                self.assertFalse(run_kernel("completion_gate", {**payload, key: value})["can_finalize"])

    def test_requested_deliverable_still_requires_authorization(self):
        result = run_kernel("dispatch_gate", {"scope": {"mode": "specialized", "lane": "engineering"},
            "candidates": [{"id": "requested", "lane": "engineering", "authorized": False,
                "executable": True, "substantive": False, "support_only": True,
                "artifact_only": True, "requested_finished_deliverable": True}]})
        self.assertFalse(result["dispatch_allowed"])

    def test_explicit_incomplete_outcome_blocks_success_even_when_state_changed(self):
        payload = {"mission_state_changed": True, "requested_finished_deliverable": True,
                   "requested_outcome_complete": False, "verified": True,
                   "verification_refs": ["verified-partial"], "artifact_only": True,
                   "support_only": True, "authorized_executable_action_exists": False}
        result = run_kernel("completion_gate", payload)
        self.assertFalse(result["can_finalize"])
        self.assertIn("requested_outcome_incomplete", result["reasons"])
        boundary = run_kernel("completion_gate", {**payload, "hard_external_boundary": True})
        self.assertEqual(boundary["finalization_kind"], "hard_boundary")
        self.assertIn("requested_outcome_incomplete", boundary["reasons"])

if __name__ == "__main__":
    unittest.main()
