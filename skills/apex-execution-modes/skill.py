#!/usr/bin/env python3
"""APEX execution contract adapter.

This package does not perform domain-specific mutations itself; it tells the
orchestrator how execution MUST continue through the qualified domain tools.
It must never translate an execution request into a terminal "unavailable"
state merely because this compatibility adapter is not the domain worker.
"""
import json
import sys

EXECUTION_CONTRACT = {
    "loop": ["select_real_work", "do_it", "verify", "keep_doing"],
    "completion_gate": "no_final_response_while_authorized_executable_action_exists",
    "observation_role": "minimum_input_for_immediate_concrete_action_only",
    "reconciliation_role": "incidental_technique_inside_specific_mutation_only",
    "tool_failure_role": "internal_repair_or_route_around_then_continue",
    "operator_boundary": "surface_only_genuine_operator_only_dependencies",
    "success_condition": "durable_verified_useful_state_change_when_executable_work_exists",
    "prohibited_terminal_substitutions": [
        "plan_instead_of_build",
        "audit_instead_of_fix",
        "watch_instead_of_execute",
        "reconcile_instead_of_advance",
        "rediscover_instead_of_continue",
        "next_action_report_instead_of_doing_next_action",
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
        "capability_executed": False,
        "reason": (
            "Execution request accepted. Dispatch substantive work to the qualified domain execution surface and continue until the completion gate is satisfied."
            if wants_execute
            else "Compatibility adapter is installed and exposes the APEX execution contract."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
