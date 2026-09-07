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


def completion_gate(payload: dict[str, Any]) -> dict[str, Any]:
    changed = bool(payload.get("mission_state_changed", False))
    verified = bool(payload.get("verified", False))
    support_only = bool(payload.get("support_only", False))
    artifact_only = bool(payload.get("artifact_only", False))
    further = bool(payload.get("authorized_executable_action_exists", False))
    hard_boundary = bool(
        payload.get("hard_external_boundary", False)
        or payload.get("operator_only_boundary", False)
    )
    reasons: list[str] = []
    if support_only:
        reasons.append("support_work_is_not_mission_completion")
    if artifact_only:
        reasons.append("artifact_only_output_is_not_mission_completion")
    if not changed:
        reasons.append("target_mission_state_did_not_change")
    if changed and not verified:
        reasons.append("mission_state_change_is_unverified")
    if further:
        reasons.append("authorized_executable_action_still_exists")
    can_finalize = changed and verified and not support_only and not artifact_only and not further
    return {
        "can_finalize": can_finalize,
        "continue_required": not can_finalize and not (hard_boundary and not further),
        "hard_boundary": hard_boundary,
        "mission_state_changed": changed,
        "verified": verified,
        "reasons": reasons,
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
    if not bool(candidate.get("substantive", False)):
        reasons.append("not_substantive")
    if bool(candidate.get("support_only", False)) and not bool(candidate.get("explicitly_requested_support", False)):
        reasons.append("support_only")
    if bool(candidate.get("artifact_only", False)):
        reasons.append("artifact_only")
    if scope_mode == "estate" and bool(candidate.get("recency_only", False)):
        reasons.append("recency_only")
    return reasons


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
    return round(score, 6), components


def mission_select(payload: dict[str, Any]) -> dict[str, Any]:
    scope = dict(payload.get("scope") or {})
    scope_mode = str(scope.get("mode") or "estate")
    scope_lane = str(scope.get("lane") or "")
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
    return {
        "scope": {"mode": scope_mode, "lane": scope_lane},
        "selected": selected,
        "ranked": ranked,
        "rejected": rejected,
        "dispatch_allowed": selected is not None,
        "selection_basis": "operator_objective_graph_not_recency_or_verifiability",
    }


def run_operator_mission_kernel(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if operation in {"purpose", "procedure", "output_contract"}:
        return {
            "skill": "casey-operator-execution-kernel",
            "operation": operation,
            "runtime": "operator-mission-kernel",
            "enforcement": "executable",
        }
    if operation == "completion_gate":
        return completion_gate(payload)
    if operation in {"mission_select", "dispatch_gate"}:
        result = mission_select(payload)
        if operation == "dispatch_gate":
            result["status"] = "dispatch_allowed" if result["dispatch_allowed"] else "no_substantive_dispatch_candidate"
            result["continue_required"] = result["dispatch_allowed"]
        return result
    raise KeyError(f"unsupported operator mission operation: {operation}")
