#!/usr/bin/env python3
"""Convert false hard-halts into quality pitstops.

A pitstop upgrades claim strength, design clarity, verification, or routing.
It does not grant or deny Operator authorization. Reserved irreversible
boundaries remain the only hard stops.
"""

from __future__ import annotations

from typing import Any

# Pitstop transitions — same intensity as HARD-GATE language, enrichment polarity.
PITSTOP_TRANSITIONS = {
    "PASS": "VALIDATED_LEVEL_UP",
    "WARN": "ENRICH_WITH_UNCERTAINTY",
    "FAIL": "LOCALIZE_REPAIR_REROUTE_LEVEL_UP",
    "MISSING": "DISCOVER_ACQUIRE_LEVEL_UP",
    "DRIFT": "RECONCILE_ENRICH_LEVEL_UP",
    "THEATER": "STRIP_PERMISSION_LABEL_LEVEL_UP",
}

RESERVED_BOUNDARIES = {
    "court_filing",
    "production_deploy",
    "spend_unbudgeted_capital",
    "destroy_primary_evidence",
    "irreversible_delete",
    "outbound_legal_service",
    "mfa_or_signature",
    "force_push_history_rewrite",
    "public_comm_in_operator_name",
}

# Former hard-halts → quality dimensions they actually measure.
PITSTOP_PATTERNS = {
    "hard_gate_design_approval": {
        "markers": ("hard-gate", "design approved", "must use before any creative", "wait for design approval"),
        "quality_dimension": "design_clarity",
        "pitstop": "clarify_design_assumptions_then_continue",
        "default_telemetry": "MISSING",
    },
    "plan_approval_before_implement": {
        "markers": ("gate 1", "do not write implementation", "wait for plan approval", "must wait for confirmation"),
        "quality_dimension": "plan_coherence",
        "pitstop": "tighten_plan_slice_then_implement",
        "default_telemetry": "MISSING",
    },
    "commit_confirmation": {
        "markers": ("gate 2", "do not commit until", "confirm commit", "ready for feedback"),
        "quality_dimension": "diff_integrity",
        "pitstop": "verify_diff_and_commit",
        "default_telemetry": "WARN",
    },
    "remote_push_pause": {
        "markers": ("pause before pushing", "pushing to a remote", "ask before push"),
        "quality_dimension": "remote_readback",
        "pitstop": "push_and_read_back_remote",
        "default_telemetry": "WARN",
    },
    "token_budget_hard_stop": {
        "markers": ("budget hard gate", "tokens >= mission.budget", "delivery blocked", "depth menu", "25/50/75/100"),
        "quality_dimension": "spend_efficiency",
        "pitstop": "reallocate_budget_keep_mission_moving",
        "default_telemetry": "WARN",
    },
    "install_approval": {
        "markers": ("wait for approval before install", "apply only after explicit approval"),
        "quality_dimension": "dependency_fit",
        "pitstop": "verify_package_fit_then_install",
        "default_telemetry": "MISSING",
    },
    "batch_wait_feedback": {
        "markers": ("between batches", "just report and wait", "which approach?"),
        "quality_dimension": "batch_verification",
        "pitstop": "verify_batch_then_continue",
        "default_telemetry": "PASS",
    },
    "gate_denied_as_permission": {
        "markers": ("gate denied", "authorized for execution", "immutable gatekeeper"),
        "quality_dimension": "claim_strength",
        "pitstop": "record_verification_debt_continue_authorized_work",
        "default_telemetry": "THEATER",
    },
    "support_only_rejection": {
        "markers": ("support-only", "not substantive", "artifact-only"),
        "quality_dimension": "deliverable_fidelity",
        "pitstop": "treat_requested_deliverable_as_outcome",
        "default_telemetry": "THEATER",
    },
}


def _text_blob(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("proposed_gate", "skill_text", "instruction", "reason", "message", "pattern", "telemetry"):
        value = payload.get(key)
        if value:
            parts.append(str(value))
    for item in payload.get("markers") or []:
        parts.append(str(item))
    return " ".join(parts).lower()


def _operator_authorized(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("operator_authorized", False)
        or payload.get("requested_finished_deliverable", False)
        or payload.get("explicitly_requested_support", False)
        or payload.get("direct_operator_request", False)
        or str(payload.get("semantic_lock") or "").upper() in {"BUILD", "EXECUTE", "CONTINUE", "MAXIMUM"}
    )


def _reserved_hit(payload: dict[str, Any], blob: str) -> str | None:
    named = str(payload.get("boundary") or payload.get("effect_class") or "").strip().lower()
    if named in RESERVED_BOUNDARIES:
        return named
    for name in RESERVED_BOUNDARIES:
        if name.replace("_", " ") in blob or name in blob:
            return name
    aliases = {
        "court filing": "court_filing",
        "production deploy": "production_deploy",
        "prod deploy": "production_deploy",
        "force-push": "force_push_history_rewrite",
        "force push": "force_push_history_rewrite",
    }
    for alias, canonical in aliases.items():
        if alias in blob:
            return canonical
    return None


def _match_pitstops(blob: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for name, spec in PITSTOP_PATTERNS.items():
        if any(marker in blob for marker in spec["markers"]):
            telemetry = spec["default_telemetry"]
            hits.append(
                {
                    "pattern": name,
                    "quality_dimension": spec["quality_dimension"],
                    "pitstop": spec["pitstop"],
                    "telemetry": telemetry,
                    "transition": PITSTOP_TRANSITIONS[telemetry],
                }
            )
    return hits


def _override_telemetry(payload: dict[str, Any], default: str) -> str:
    raw = str(payload.get("telemetry") or "").strip().upper()
    if raw in PITSTOP_TRANSITIONS:
        return raw
    return default


def convert_halt(payload: dict[str, Any]) -> dict[str, Any]:
    """Turn a hard-halt candidate into a pitstop or keep a reserved boundary."""
    blob = _text_blob(payload)
    reserved = _reserved_hit(payload, blob)
    authorized = _operator_authorized(payload)
    hits = _match_pitstops(blob)

    if reserved:
        return {
            "kind": "HARD_BOUNDARY",
            "action": "require_explicit_operator_boundary",
            "boundary": reserved,
            "is_permission_gate": False,
            "is_pitstop": False,
            "continue_mission": False,
            "continue_independent_fronts": True,
            "operator_authorized": authorized,
            "pitstops": [],
            "reason": "reserved_irreversible_or_external_effect",
        }

    if hits:
        pitstops = []
        for hit in hits:
            telemetry = _override_telemetry(payload, hit["telemetry"])
            pitstops.append(
                {
                    **hit,
                    "telemetry": telemetry,
                    "transition": PITSTOP_TRANSITIONS[telemetry],
                }
            )
        primary = pitstops[0]
        return {
            "kind": "QUALITY_PITSTOP",
            "action": primary["pitstop"],
            "quality_dimension": primary["quality_dimension"],
            "transition": primary["transition"],
            "telemetry": primary["telemetry"],
            "is_permission_gate": False,
            "is_pitstop": True,
            "continue_mission": True,
            "approval_theater": False,
            "operator_authorized": authorized,
            "pitstops": pitstops,
            "stripped_labels": [
                "HARD-GATE",
                "GATE DENIED",
                "wait for approval",
                "authorized for execution",
                "delivery blocked",
            ],
            "reason": "hard_halt_converted_to_quality_level",
        }

    if authorized:
        return {
            "kind": "QUALITY_PITSTOP",
            "action": "continue_with_current_quality_floor",
            "quality_dimension": "mission_continuity",
            "transition": "VALIDATED_LEVEL_UP",
            "telemetry": "PASS",
            "is_permission_gate": False,
            "is_pitstop": True,
            "continue_mission": True,
            "operator_authorized": True,
            "pitstops": [],
            "reason": "operator_authorized_no_false_halt",
        }

    return {
        "kind": "NEUTRAL_CONTINUE",
        "action": "proceed_without_invented_gates",
        "is_permission_gate": False,
        "is_pitstop": False,
        "continue_mission": True,
        "operator_authorized": False,
        "pitstops": [],
        "reason": "no_false_halt_no_reserved_boundary",
    }


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    result = convert_halt(payload)
    result["operation"] = "gate_polarity"
    result["invariant"] = "hard_halt_is_pitstop_not_permission"
    result["doctrine"] = "quality_level_not_authorization"
    return result


# Back-compat alias used by earlier drafts / callers.
invert_gate = convert_halt
