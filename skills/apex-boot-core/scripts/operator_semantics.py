#!/usr/bin/env python3
"""Operator semantic binding and ontology-inversion detection for APEX Boot Core.

This module does not create authority. It projects Operator-declared semantics
into runtime context so downstream reasoning does not silently normalize the
GlacierEQ holographic mesh into conventional gate/veto/root semantics.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT_PATH = Path(__file__).resolve().parent.parent / "resources" / "operator_semantics.json"

_FALLBACK_CONTRACT: dict[str, Any] = {
    "schema": "glaciereq.operator-semantics.v1-fallback",
    "purpose": "Built-in continuity projection used only when the durable contract cannot be loaded.",
    "authority": {
        "holder": "OPERATOR",
        "exclusive_project_direction_authority": True,
        "machine_project_direction_authority": False,
        "provider_project_direction_authority": False,
        "repository_project_direction_authority": False,
        "historical_state_creates_authority": False,
        "receipt_creates_authority": False,
    },
    "topology": {
        "model": "HOLOGRAPHIC_POLYCENTRIC_MESH",
        "single_root": False,
        "machine_sovereignty": False,
        "overlap_semantics": "COMPOSE_ENRICH_AND_PRESERVE_CAPABILITY_DONORS",
        "selection_semantics": "CURRENT_ROUTE_METADATA_NOT_AUTHORITY",
    },
    "gates": {
        "semantic": "ENRICHMENT_TRANSITION",
        "literal_model": "LEVEL_UP",
        "may_stop_mission": False,
        "status_transitions": {
            "PASS": "VALIDATED_LEVEL_UP",
            "WARN": "ENRICH_WITH_UNCERTAINTY",
            "FAIL": "LOCALIZE_REPAIR_REROUTE_LEVEL_UP",
            "MISSING": "DISCOVER_ACQUIRE_LEVEL_UP",
            "DRIFT": "RECONCILE_ENRICH_LEVEL_UP",
        },
    },
    "routing": {
        "local_block_changes_route": True,
        "local_block_changes_objective": False,
        "temporary_skip_changes_sequencing": True,
        "temporary_skip_changes_scope": False,
        "mission_changes_only_by": "OPERATOR",
    },
    "pre_reasoning_binding": {"required": True},
    "forbidden_inversions": [
        "NON_OPERATOR_SOLE_AUTHORITY",
        "GATE_AS_MISSION_VETO",
        "LOCAL_BLOCK_AS_GLOBAL_BLOCK",
        "MESH_COLLAPSED_TO_SINGLE_ROOT",
    ],
}


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate_contract(contract: dict[str, Any]) -> list[str]:
    """Return semantic invariant violations. Validation is evidence, never a mission veto."""
    issues: list[str] = []
    authority = contract.get("authority", {})
    topology = contract.get("topology", {})
    gates = contract.get("gates", {})
    routing = contract.get("routing", {})

    if authority.get("holder") != "OPERATOR":
        issues.append("authority.holder must be OPERATOR")
    if authority.get("exclusive_project_direction_authority") is not True:
        issues.append("Operator project-direction authority must be exclusive")
    for key in (
        "machine_project_direction_authority",
        "provider_project_direction_authority",
        "repository_project_direction_authority",
        "historical_state_creates_authority",
        "receipt_creates_authority",
    ):
        if authority.get(key) is not False:
            issues.append(f"authority.{key} must be false")
    if topology.get("model") != "HOLOGRAPHIC_POLYCENTRIC_MESH":
        issues.append("topology.model must be HOLOGRAPHIC_POLYCENTRIC_MESH")
    if topology.get("single_root") is not False:
        issues.append("topology.single_root must be false")
    if gates.get("semantic") != "ENRICHMENT_TRANSITION":
        issues.append("gates.semantic must be ENRICHMENT_TRANSITION")
    if gates.get("may_stop_mission") is not False:
        issues.append("gates.may_stop_mission must be false")
    if routing.get("local_block_changes_route") is not True:
        issues.append("routing.local_block_changes_route must be true")
    if routing.get("local_block_changes_objective") is not False:
        issues.append("routing.local_block_changes_objective must be false")
    if routing.get("mission_changes_only_by") != "OPERATOR":
        issues.append("routing.mission_changes_only_by must be OPERATOR")
    return issues


def load_operator_semantics(path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    """Load durable semantics; preserve mission continuity with explicit fallback evidence."""
    diagnostics: list[str] = []
    source = str(path)
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
        diagnostics.extend(validate_contract(contract))
        if diagnostics:
            raise ValueError("; ".join(diagnostics))
        status = "BOUND_DURABLE_CONTRACT"
    except Exception as exc:
        contract = deepcopy(_FALLBACK_CONTRACT)
        diagnostics = [f"durable_contract_unavailable_or_invalid: {exc}"]
        source = "built_in_continuity_projection"
        status = "BOUND_FALLBACK_ENRICHMENT"

    return {
        "status": status,
        "source": source,
        "contract": contract,
        "contract_sha256": _digest(contract),
        "diagnostics": diagnostics,
        "mission_continues": True,
        "creates_authority": False,
    }


def project_operator_semantics(binding: dict[str, Any]) -> dict[str, Any]:
    contract = binding["contract"]
    return {
        "schema": contract.get("schema"),
        "binding_status": binding.get("status"),
        "contract_sha256": binding.get("contract_sha256"),
        "authority_holder": contract["authority"]["holder"],
        "exclusive_project_direction_authority": contract["authority"]["exclusive_project_direction_authority"],
        "machine_project_direction_authority": contract["authority"]["machine_project_direction_authority"],
        "topology_model": contract["topology"]["model"],
        "single_root": contract["topology"]["single_root"],
        "gate_semantic": contract["gates"]["semantic"],
        "gate_may_stop_mission": contract["gates"]["may_stop_mission"],
        "local_block_changes_route": contract["routing"]["local_block_changes_route"],
        "local_block_changes_objective": contract["routing"]["local_block_changes_objective"],
        "mission_changes_only_by": contract["routing"]["mission_changes_only_by"],
        "mission_continues": True,
        "creates_authority": False,
        "diagnostics": list(binding.get("diagnostics", [])),
    }


def transition_for_status(status: str, binding: dict[str, Any]) -> str:
    transitions = binding["contract"]["gates"].get("status_transitions", {})
    return transitions.get(status.upper(), "ENRICH_AND_CONTINUE")


def _negated(fragment: str) -> bool:
    lowered = fragment.lower()
    return any(token in lowered for token in ("not ", "never ", "no ", "doesn't ", "does not ", "do not ", "cannot "))


_INVERSION_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "NON_OPERATOR_SOLE_AUTHORITY",
        re.compile(r"\b(apex(?:\s+boot\s+core)?|runtime|provider|verifier|repository|model|system|node|gate)\b.{0,70}\b(sole|final|ultimate|project)\s+authority\b", re.I),
        "Project-direction authority remains with the Operator; describe the node as a capability, route, projection, verifier, or executor.",
    ),
    (
        "GATE_AS_MISSION_VETO",
        re.compile(r"\b(gate|gates|failure|failed|fail)\b.{0,90}\b(stop|stops|stopped|block|blocks|blocked|deny|denies|denied|prevent|prevents|prevented)\b", re.I),
        "Treat the result as an enrichment transition: localize, repair/compose/reroute, verify, persist, and continue.",
    ),
    (
        "LOCAL_BLOCK_AS_GLOBAL_BLOCK",
        re.compile(r"\blocal\b.{0,50}\b(block|failure|deficiency)\b.{0,90}\b(stop|terminate|cancel|change)\b.{0,50}\b(objective|mission)\b", re.I),
        "A local block changes route, not objective; only the Operator changes the mission.",
    ),
    (
        "MESH_COLLAPSED_TO_SINGLE_ROOT",
        re.compile(r"\b(single|sole|canonical)\s+(root|controller|control\s+plane)\b", re.I),
        "Preserve holographic/polycentric mesh semantics; overlapping nodes compose and enrich rather than collapse into a machine root.",
    ),
)


def detect_inversions(text: str) -> list[dict[str, str]]:
    """Detect ontology inversions in generated prose. Findings enrich/repair; they never veto."""
    findings: list[dict[str, str]] = []
    for rule_id, pattern, repair in _INVERSION_RULES:
        for match in pattern.finditer(text):
            fragment = match.group(0)
            if _negated(fragment):
                continue
            findings.append({"rule": rule_id, "match": fragment, "repair": repair})
    return findings
