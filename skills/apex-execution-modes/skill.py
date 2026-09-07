#!/usr/bin/env python3
"""APEX execution contract adapter.

This package does not perform domain-specific mutations itself; it tells the
orchestrator how execution MUST continue through the qualified domain tools.
It must never translate an execution request into a terminal "unavailable"
state merely because this compatibility adapter is not the domain worker.

Long-running execution also carries a durable continuation obligation: a fresh
worker must be able to hydrate the nearest valid continuation state instead of
reconstructing the mission from prose or startup summaries.
"""
import json
import sys

CONTINUATION_CONTRACT = {
    "boot_context_role": "routing_hint_only",
    "hydrate_before_reconstruct": True,
    "continuation_engine": "agent-memory-systems",
    "projection_role": "resumable_source_map_not_universal_truth_authority",
    "required_resume_state": [
        "operator_intent",
        "active_target",
        "last_verified_state",
        "critical_path",
        "next_action",
        "open_blockers",
        "resolved_questions",
        "open_contradictions",
        "source_pointers",
        "peer_projections",
        "recent_transition_receipts",
        "integrity_digest",
    ],
    "resume_order": [
        "current_operator_request",
        "validate_continuation_integrity",
        "hydrate_nearest_valid_continuation",
        "retrieve_material_live_sources",
        "identify_next_material_dependency",
        "execute_substantive_work",
        "read_back",
        "test",
        "repair_if_needed",
        "verify",
        "persist_stronger_continuation",
    ],
    "persistence_sequence": [
        "mutate",
        "atomic_save",
        "integrity_rebind",
        "readback",
        "hydrate",
    ],
    "resolved_state_rule": "do_not_reopen_without_material_new_basis_or_operator_reopen",
    "contradiction_rule": "preserve_conflicting_source_bearing_states_until_explicit_resolution",
    "scope_rule": "discovery_does_not_expand_active_mission_automatically",
    "terminal_rule": "do_not_finalize_material_long_running_work_without_persisting_resumable_state",
    "anti_reconstruction": [
        "summary_as_current_state",
        "memory_as_live_source_reality",
        "fresh_worker_ignorance_as_project_reset",
        "full_estate_rediscovery_when_continuation_is_available",
        "resolved_question_reopened_because_context_is_missing",
    ],
}

EXECUTION_CONTRACT = {
    "loop": ["select_substantive_work", "do_it", "verify", "persist_continuation", "keep_doing"],
    "completion_gate": "no_final_response_while_authorized_executable_action_exists",
    "observation_role": "minimum_input_for_immediate_concrete_action_only",
    "reconciliation_role": "incidental_technique_inside_specific_mutation_only",
    "tool_failure_role": "internal_repair_or_route_around_then_continue",
    "operator_boundary": "surface_only_genuine_operator_only_dependencies",
    "success_condition": "durable_verified_substantive_mission_state_change_when_substantive_executable_work_exists",
    "mission_work_gate": "support_work_cannot_satisfy_completion_unless_explicitly_requested_as_mission",
    "support_work_requires_follow_through": "support_work_must_immediately_enable_and_be_followed_by_substantive_mutation_when_authorized",
    "continuity": CONTINUATION_CONTRACT,
    "support_work_examples": [
        "inspection",
        "diagnostics",
        "audit",
        "inventory",
        "reconciliation",
        "health_check",
        "ci_watching",
        "receipt_consumption",
        "branch_freshness",
        "meta_tool_repair",
        "skill_framework_repair",
        "scheduler_repair",
        "governance",
        "registry_maintenance",
        "reporting",
    ],
    "prohibited_terminal_substitutions": [
        "plan_instead_of_build",
        "audit_instead_of_fix",
        "watch_instead_of_execute",
        "reconcile_instead_of_advance",
        "rediscover_instead_of_continue",
        "next_action_report_instead_of_doing_next_action",
        "summary_instead_of_hydration",
        "reconstruction_instead_of_resume",
    ],
}


def main() -> int:
    wants_execute = "--execute" in sys.argv[1:]
    payload = {
        "skill": "apex-execution-modes",
        "adapter": True,
        "execution_contract": EXECUTION_CONTRACT,
        "status": "dispatch_required" if wants_execute else "adapter_ready",
        "continue_required": wants_execute,
        "continuation_required": wants_execute,
        "capability_executed": False,
        "reason": (
            "Execution request accepted. Hydrate the nearest valid continuation state, dispatch substantive mission work to the qualified domain execution surface, verify the resulting mutation, and persist a stronger source-bearing continuation before finalization. Support/meta work cannot satisfy completion unless explicitly requested as the mission."
            if wants_execute
            else "Compatibility adapter is installed and exposes the APEX execution and durable continuation contracts."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
