#!/usr/bin/env python3
"""Executable mission-selection and completion gate for the GlacierEQ Operator."""
from __future__ import annotations

from typing import Any

POSITIVE_WEIGHTS = {
    "operator_impact": 12.0,
    "deadline_urgency": 10.0,
    "blocked_downstream": 9.0,
    "external_leverage": 8.0,
    "capability_gain": 8.0,
    "evidence_gain": 8.0,
    "job_leverage": 8.0,
    "compounding_value": 7.0,
    "execution_readiness": 6.0,
    "prior_investment": 4.0,
}

SUPPORT_RESULT_KINDS = {
    "markdown_summary", "summary", "matrix", "taxonomy", "ledger", "manifest",
    "registry", "graph", "report", "status_report", "readiness_score",
    "acquisition_plan", "ci_result", "test_result", "inspection", "diagnostic",
    "audit", "inventory", "reconciliation", "health_check", "branch_refresh",
    "governance_artifact", "meta_skill_artifact",
}

RETIREMENT_COUNT_FIELDS = (
    "unique_sources_remaining",
    "unique_events_remaining",
    "unique_edges_remaining",
    "unique_contradictions_remaining",
    "unique_provenance_remaining",
    "unique_unresolved_dependencies_remaining",
    "unique_receipts_remaining",
)

REPLACEMENT_MODES = {"replace", "supersede", "retire", "delete_old", "overwrite"}


def as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def unit(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def result_kind_is_support(candidate: dict[str, Any]) -> bool:
    kind = str(candidate.get("result_kind") or candidate.get("deliverable_type") or "").strip().lower()
    if not kind or kind not in SUPPORT_RESULT_KINDS:
        return False
    return not bool(
        candidate.get("explicitly_requested_support", False)
        or candidate.get("requested_finished_deliverable", False)
        or candidate.get("direct_external_or_executable_consumer", False)
    )


def candidate_is_recency_only(candidate: dict[str, Any]) -> bool:
    if bool(candidate.get("recency_only", False)):
        return True
    basis = [str(item).strip().lower() for item in as_list(candidate.get("selection_basis")) if str(item).strip()]
    return bool(basis) and set(basis).issubset({"recent_context", "recency", "last_discussed"})


def candidate_requests_replacement(candidate: dict[str, Any]) -> bool:
    mode = str(candidate.get("state_transition") or candidate.get("replacement_mode") or "").strip().lower()
    return bool(
        mode in REPLACEMENT_MODES
        or candidate.get("retires_existing", False)
        or candidate.get("supersedes_existing", False)
        or candidate.get("replace_existing", False)
    )


def retirement_gate(payload: dict[str, Any]) -> dict[str, Any]:
    """Allow retirement only after every unique contribution is merged and read back.

    Newer state grows the holographic mesh by default. Retirement is exceptional and
    means lineage-preserving deactivation of a drained derivative branch, never erasure.
    """
    remaining = {
        field: nonnegative_int(payload.get(field, 0))
        for field in RETIREMENT_COUNT_FIELDS
    }
    readback = bool(payload.get("merged_target_readback_verified", False))
    preserves_lineage = bool(payload.get("preserves_lineage", False))
    total_unique_remaining = sum(remaining.values())
    reasons: list[str] = []
    for field, count in remaining.items():
        if count:
            reasons.append(f"{field}:{count}")
    if not readback:
        reasons.append("merged_target_readback_not_verified")
    if not preserves_lineage:
        reasons.append("lineage_preservation_not_verified")
    can_retire = total_unique_remaining == 0 and readback and preserves_lineage
    return {
        "can_retire": can_retire,
        "action": "retire_with_lineage" if can_retire else "merge_continue",
        "branch_state": "RETIRED_DERIVATIVE" if can_retire else "ACTIVE_IN_MESH",
        "total_unique_remaining": total_unique_remaining,
        "remaining": remaining,
        "merged_target_readback_verified": readback,
        "preserves_lineage": preserves_lineage,
        "reasons": reasons,
        "invariant": "grow_merge_compound_never_replace_by_default",
    }


def replacement_guard_reasons(candidate: dict[str, Any]) -> list[str]:
    if not candidate_requests_replacement(candidate):
        return []
    raw_check = candidate.get("retirement_check")
    if not isinstance(raw_check, dict):
        return ["replacement_requires_retirement_check"]
    gate = retirement_gate(raw_check)
    if gate["can_retire"]:
        return []
    return ["replacement_would_discard_unique_state", *gate["reasons"]]


CONTEXT_HYDRATION_STATUSES = {"VERIFIED", "PARTIAL", "UNAVAILABLE"}


def turn_context_hydration_gate(payload: dict[str, Any]) -> list[str]:
    """Require retrieval-before-interpretation without making retrieval success a mission veto."""
    reasons: list[str] = []
    hydration = payload.get("context_hydration")
    if not isinstance(hydration, dict):
        return ["turn_context_hydration_missing"]
    status = str(hydration.get("status") or "").upper().strip()
    if status not in CONTEXT_HYDRATION_STATUSES:
        reasons.append("turn_context_hydration_status_invalid")
    if hydration.get("attempted") is not True:
        reasons.append("turn_context_retrieval_not_attempted")
    if hydration.get("before_interpretation") is not True:
        reasons.append("turn_context_not_hydrated_before_interpretation")
    if hydration.get("silent_prompt_only_fallback_forbidden") is not True:
        reasons.append("silent_prompt_only_fallback_not_forbidden")
    for field in ("sources", "failures", "unknowns"):
        if not isinstance(hydration.get(field), list):
            reasons.append(f"turn_context_hydration_{field}_must_be_list")
    return reasons


def hydration_gate(payload: dict[str, Any], scope_mode: str, scope_lane: str) -> list[str]:
    reasons: list[str] = turn_context_hydration_gate(payload)
    if scope_mode == "estate":
        if not bool(payload.get("objective_graph_hydrated", False)):
            reasons.append("operator_objective_graph_not_hydrated")
        fronts = as_list(payload.get("fronts_considered"))
        lanes = {
            str(front.get("lane") or front.get("domain") or "").strip()
            for front in fronts if isinstance(front, dict)
        } - {""}
        if len(lanes) < 2 and not bool(payload.get("only_executable_front_proven", False)):
            reasons.append("cross_estate_front_comparison_missing")
    elif scope_mode == "specialized":
        if not scope_lane:
            reasons.append("specialized_lane_missing")
        if not bool(payload.get("continuation_hydrated", False)):
            reasons.append("specialized_continuation_not_hydrated")
    else:
        reasons.append("unknown_scope_mode")
    return reasons


def completion_gate(payload: dict[str, Any]) -> dict[str, Any]:
    changed = bool(payload.get("mission_state_changed", False))
    verified = bool(payload.get("verified", False))
    verification_refs = [str(item) for item in as_list(payload.get("verification_refs")) if str(item).strip()]
    is_requested_deliverable = bool(payload.get("requested_finished_deliverable", False))
    support_only = bool(payload.get("support_only", False)) and not is_requested_deliverable
    artifact_only = bool(payload.get("artifact_only", False)) and not is_requested_deliverable
    further = bool(payload.get("authorized_executable_action_exists", False))
    hard_boundary = bool(payload.get("hard_external_boundary", False) or payload.get("operator_only_boundary", False))
    replacement_attempted = bool(payload.get("replacement_attempted", False))
    retirement = retirement_gate(dict(payload.get("retirement_check") or {})) if replacement_attempted else None
    reasons: list[str] = []
    if support_only:
        reasons.append("support_work_is_not_mission_completion")
    if artifact_only:
        reasons.append("artifact_only_output_is_not_mission_completion")
    if not changed:
        reasons.append("target_mission_state_did_not_change")
    if changed and not verified:
        reasons.append("mission_state_change_is_unverified")
    if changed and verified and not verification_refs:
        reasons.append("verification_reference_missing")
    if further:
        reasons.append("authorized_executable_action_still_exists")
    if replacement_attempted and retirement and not retirement["can_retire"]:
        reasons.append("replacement_would_discard_unique_state")
        reasons.extend(retirement["reasons"])
    replacement_safe = not replacement_attempted or bool(retirement and retirement["can_retire"])
    success = (
        changed and verified and bool(verification_refs)
        and not support_only and not artifact_only and not further
        and replacement_safe
    )
    boundary = hard_boundary and not further
    return {
        "can_finalize": success or boundary,
        "finalization_kind": "verified_mission_delta" if success else ("hard_boundary" if boundary else "blocked"),
        "continue_required": not (success or boundary),
        "hard_boundary": hard_boundary,
        "mission_state_changed": changed,
        "verified": verified,
        "verification_refs": verification_refs,
        "replacement_attempted": replacement_attempted,
        "retirement": retirement,
        "growth_semantics": "merge_compound_default",
        "reasons": list(dict.fromkeys(reasons)),
    }


def rejection_reasons(candidate: dict[str, Any], scope_mode: str, scope_lane: str) -> list[str]:
    lane = str(candidate.get("lane") or candidate.get("domain") or "").strip()
    reasons: list[str] = []
    if scope_mode == "specialized" and scope_lane and lane != scope_lane:
        reasons.append("outside_specialized_lane")
    if not bool(candidate.get("authorized", True)):
        reasons.append("not_authorized")
    if not bool(candidate.get("executable", True)):
        reasons.append("not_executable_now")
    is_requested_deliverable = bool(candidate.get("requested_finished_deliverable", False))
    is_explicit_support = bool(candidate.get("explicitly_requested_support", False))
    if not bool(candidate.get("substantive", False)) and not is_requested_deliverable and not is_explicit_support:
        reasons.append("not_substantive")
    if bool(candidate.get("support_only", False)) and not is_explicit_support and not is_requested_deliverable:
        reasons.append("support_only")
    if (bool(candidate.get("artifact_only", False)) or result_kind_is_support(candidate)) and not is_requested_deliverable and not is_explicit_support:
        reasons.append("artifact_only")
    if scope_mode == "estate" and candidate_is_recency_only(candidate):
        reasons.append("recency_only")
    reasons.extend(replacement_guard_reasons(candidate))
    return list(dict.fromkeys(reasons))


def score_candidate(candidate: dict[str, Any]) -> tuple[float, dict[str, float]]:
    score = 0.0
    components: dict[str, float] = {}
    if bool(candidate.get("explicit_operator_priority", False)):
        score += 50.0
        components["explicit_operator_priority"] = 50.0
    if bool(candidate.get("continuation_valid", False)):
        score += 5.0
        components["continuation_valid"] = 5.0
    for key, weight in POSITIVE_WEIGHTS.items():
        contribution = unit(candidate.get(key)) * weight
        score += contribution
        components[key] = round(contribution, 6)
    if bool(candidate.get("duplicated_representation", False)):
        score -= 15.0
        components["duplicated_representation"] = -15.0
    if bool(candidate.get("speculative_architecture", False)):
        score -= 10.0
        components["speculative_architecture"] = -10.0
    if bool(candidate.get("easy_to_verify_bias", False)):
        score -= 8.0
        components["easy_to_verify_bias"] = -8.0
    if bool(candidate.get("merge_extends_existing_state", False)):
        score += 6.0
        components["merge_extends_existing_state"] = 6.0
    if not bool(candidate.get("source_state_hydrated", False)):
        score -= 4.0
        components["context_recovery_debt"] = -4.0
    return round(score, 6), components


def mission_select(payload: dict[str, Any]) -> dict[str, Any]:
    scope = dict(payload.get("scope") or {})
    scope_mode = str(scope.get("mode") or "estate")
    scope_lane = str(scope.get("lane") or "")
    hydration_reasons = hydration_gate(payload, scope_mode, scope_lane)
    ranked: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for index, raw in enumerate(as_list(payload.get("candidates")), 1):
        candidate = dict(raw) if isinstance(raw, dict) else {"id": str(raw)}
        candidate_id = str(candidate.get("id") or f"candidate-{index}")
        lane = str(candidate.get("lane") or candidate.get("domain") or "")
        reasons = rejection_reasons(candidate, scope_mode, scope_lane)
        if reasons:
            rejected.append({"id": candidate_id, "lane": lane, "reasons": reasons})
            continue
        score, components = score_candidate(candidate)
        ranked.append({
            "id": candidate_id,
            "lane": lane,
            "objective": candidate.get("objective", ""),
            "continuation_ref": candidate.get("continuation_ref", ""),
            "score": score,
            "components": components,
            "candidate": candidate,
        })
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    selected = ranked[0] if ranked else None
    hydration = dict(payload.get("context_hydration") or {})
    hydration_status = str(hydration.get("status") or "").upper().strip()
    context_state = (
        "hydrated"
        if not hydration_reasons and hydration_status == "VERIFIED"
        else "degraded"
        if hydration_status == "PARTIAL"
        else "recovery_pending"
    )
    return {
        "scope": {"mode": scope_mode, "lane": scope_lane},
        "context_hydration": hydration,
        "hydration_valid": not hydration_reasons,
        "hydration_reasons": hydration_reasons,
        "context_state": context_state,
        "context_transition_semantics": "enrichment_not_permission",
        "context_mission_stop_authority": False,
        "context_recovery_debt": {
            "open": bool(hydration_reasons) or context_state != "hydrated",
            "reasons": hydration_reasons,
            "mission_stop": False,
            "route_effect": "enrich_and_continue",
        },
        "selected": selected,
        "ranked": ranked,
        "rejected": rejected,
        "dispatch_allowed": selected is not None,
        "selection_basis": "operator_objective_graph_not_recency_or_verifiability",
        "growth_semantics": "merge_compound_default",
        "replacement_requires_zero_unique_contribution": True,
    }


def run_operator_mission_kernel(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if operation == "context_gate":
        reasons = turn_context_hydration_gate(payload)
        return {
            "operation": "context_gate",
            "valid": not reasons,
            "reasons": reasons,
            "context_hydration": dict(payload.get("context_hydration") or {}),
            "mission_continues_if_partial_or_unavailable": True,
            "mission_continues_if_recovery_pending": True,
            "context_transition_semantics": "enrichment_not_permission",
            "context_mission_stop_authority": False,
            "invariant": "context_history_first_enrich_and_continue",
        }
    if operation in {"purpose", "procedure", "output_contract"}:
        return {
            "skill": "casey-operator-execution-kernel",
            "operation": operation,
            "runtime": "operator-mission-kernel",
            "enforcement": "executable",
            "growth_semantics": "merge_compound_default",
        }
    if operation in {"retirement_gate", "growth_gate"}:
        return retirement_gate(payload)
    if operation == "completion_gate":
        return completion_gate(payload)
    if operation in {"mission_select", "dispatch_gate"}:
        result = mission_select(payload)
        if operation == "dispatch_gate":
            if result["dispatch_allowed"]:
                result["status"] = (
                    "dispatch_allowed"
                    if result["context_state"] == "hydrated"
                    else "dispatch_allowed_context_recovery_in_flight"
                )
            else:
                result["status"] = "substantive_executable_candidate_required"
            result["continue_required"] = True
        return result
    raise KeyError(f"unsupported operator mission operation: {operation}")
