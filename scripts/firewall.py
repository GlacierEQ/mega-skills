"""Read-only action firewall for Mega Skill mission execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FirewallViolation(PermissionError):
    """Raised when a mission attempts an action outside its declared policy."""


ALLOWED_ACTIONS = {
    "read_repository",
    "run_local_tests",
    "write_run_artifacts",
    "emit_receipt",
}
REQUIRED_FORBIDDEN = {
    "external_mutation",
    "network_send",
    "file_submission",
    "deletion",
    "deployment",
    "merge",
    "credential_access",
    "legal_filing",
    "autonomous_legal_decision",
    "execute_unknown_program",
}
REQUIRED_EVIDENCE = {"input_manifest", "phase_receipts", "output_manifest", "failure_record"}


def _unique_strings(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and len(value) == len(set(value))
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate_policy(policy: dict[str, Any], mega_id: str | None = None) -> None:
    """Validate the complete contract, not merely the fields the runner happens to use."""
    required = {
        "schema_version", "mega_id", "mode", "allowed_actions",
        "approval_required_for", "forbidden_actions", "required_evidence",
        "human_control",
    }
    if not isinstance(policy, dict):
        raise ValueError("firewall policy must be an object")
    missing = required - policy.keys()
    if missing:
        raise ValueError(f"firewall policy missing fields: {sorted(missing)}")
    if policy["schema_version"] != 1:
        raise ValueError("unsupported firewall schema version")
    if mega_id is not None and policy["mega_id"] != mega_id:
        raise ValueError("firewall policy Mega ID does not match registry")
    if policy["mode"] != "read_only":
        raise ValueError("Mega firewall mode must be read_only")
    for field in ("allowed_actions", "approval_required_for", "forbidden_actions", "required_evidence"):
        if not _unique_strings(policy[field]):
            raise ValueError(f"firewall {field} must be a non-empty unique string list")
    if set(policy["allowed_actions"]) != ALLOWED_ACTIONS:
        raise ValueError("firewall allowed_actions must be exactly the safe local action set")
    forbidden = set(policy["forbidden_actions"])
    approval = set(policy["approval_required_for"])
    if not REQUIRED_FORBIDDEN.issubset(forbidden):
        raise ValueError("firewall is missing mandatory forbidden actions")
    if not REQUIRED_FORBIDDEN.issubset(approval):
        raise ValueError("firewall is missing approval requirements for mandatory denials")
    if set(policy["allowed_actions"]) & forbidden:
        raise ValueError("firewall action cannot be both allowed and forbidden")
    if not REQUIRED_EVIDENCE.issubset(set(policy["required_evidence"])):
        raise ValueError("firewall is missing mandatory evidence requirements")
    if policy["human_control"] != "required":
        raise ValueError("firewall must require human control")


def load_policy(root: Path, mega_id: str) -> dict[str, Any]:
    registry_path = root / "registry" / "mega-skills.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    entry = next((item for item in data.get("entries", []) if item.get("id") == mega_id), None)
    if entry is None:
        raise ValueError(f"unknown Mega Skill: {mega_id}")
    policy = entry.get("firewall")
    if not isinstance(policy, dict):
        raise ValueError(f"{mega_id}: firewall policy is missing")
    validate_policy(policy, mega_id)
    return policy


def guard(policy: dict[str, Any], action: str) -> None:
    """Validate the policy and permit only an explicitly safe local action."""
    validate_policy(policy)
    if action in policy["forbidden_actions"] or action not in policy["allowed_actions"]:
        raise FirewallViolation(f"firewall denied action: {action}")
