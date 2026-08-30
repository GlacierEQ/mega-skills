"""Read-only action firewall for Mega Skill mission execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FirewallViolation(PermissionError):
    """Raised when a mission attempts an action outside its declared policy."""


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
ALLOWED_ACTIONS = {"read_repository", "run_local_tests", "write_run_artifacts", "emit_receipt"}


def validate_policy(policy: dict[str, Any], mega_id: str | None = None) -> None:
    required = {
        "schema_version", "mega_id", "mode", "allowed_actions",
        "approval_required_for", "forbidden_actions", "required_evidence",
        "human_control",
    }
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
        value = policy[field]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            raise ValueError(f"firewall {field} must be a non-empty string list")
    if not set(policy["allowed_actions"]).issubset(ALLOWED_ACTIONS):
        raise ValueError("firewall allows an unapproved action")
    if not REQUIRED_FORBIDDEN.issubset(policy["forbidden_actions"]):
        raise ValueError("firewall is missing mandatory forbidden actions")
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
    """Permit only explicitly safe local actions; deny everything else."""
    if action in policy.get("forbidden_actions", []) or action not in policy.get("allowed_actions", []):
        raise FirewallViolation(f"firewall denied action: {action}")
