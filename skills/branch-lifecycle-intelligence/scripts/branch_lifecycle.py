#!/usr/bin/env python3
"""Deterministic branch lifecycle classifier and cleanup planner."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "glaciereq.branch-lifecycle-plan.v1"
INVENTORY_SCHEMA = "glaciereq.branch-inventory.v1"
DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "resources" / "policy.json"

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload

def load_policy(path: Path | None) -> dict[str, Any]:
    policy = load_json(path or DEFAULT_POLICY)
    required = {
        "version",
        "stale_days",
        "minimum_delete_confidence",
        "protected_patterns",
        "automatic_delete_states",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise ValueError(f"policy missing fields: {', '.join(missing)}")
    return policy

def validate_inventory(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != INVENTORY_SCHEMA:
        errors.append(f"schema must be {INVENTORY_SCHEMA}")
    if not isinstance(payload.get("repository"), str) or "/" not in payload["repository"]:
        errors.append("repository must be owner/name")
    if not isinstance(payload.get("default_branch"), str) or not payload["default_branch"]:
        errors.append("default_branch is required")
    if parse_time(payload.get("generated_at")) is None:
        errors.append("generated_at must be an ISO-8601 timestamp")
    branches = payload.get("branches")
    if not isinstance(branches, list):
        errors.append("branches must be an array")
        return errors
    seen: set[str] = set()
    for index, branch in enumerate(branches):
        label = f"branches[{index}]"
        if not isinstance(branch, dict):
            errors.append(f"{label} must be an object")
            continue
        name = branch.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{label}.name is required")
            continue
        if name in seen:
            errors.append(f"duplicate branch name: {name}")
        seen.add(name)
        if not isinstance(branch.get("protected"), bool):
            errors.append(f"{label}.protected must be boolean")
        for field in ("ahead_by", "behind_by"):
            value = branch.get(field)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                errors.append(f"{label}.{field} must be a non-negative integer or null")
        for field in ("open_prs", "merged_prs", "closed_unmerged_prs", "evidence_errors"):
            value = branch.get(field, [])
            if not isinstance(value, list):
                errors.append(f"{label}.{field} must be an array")
    return errors

def is_protected(name: str, branch: dict[str, Any], default_branch: str, policy: dict[str, Any]) -> bool:
    if name == default_branch or bool(branch.get("protected")):
        return True
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in policy["protected_patterns"])

def family_key(name: str, policy: dict[str, Any]) -> str:
    value = name.strip().lower()
    for prefix in policy.get("family_prefixes", []):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    value = re.sub(r"(?<!\d)20\d{6}(?!\d)", "", value)
    value = re.sub(r"(?<!\d)20\d{2}[-_.]?\d{2}[-_.]?\d{2}(?!\d)", "", value)
    value = re.sub(r"(?:^|[-_/])(pr|issue|run|ticket)[-_]?\d+(?=$|[-_/])", "-", value)
    value = re.sub(r"[-_/]\d{5,}$", "", value)
    value = re.sub(r"[-_/]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value or name.lower()

def classify(
    branch: dict[str, Any],
    *,
    default_branch: str,
    generated_at: datetime,
    policy: dict[str, Any],
) -> dict[str, Any]:
    name = str(branch["name"])
    evidence_errors = [str(x) for x in branch.get("evidence_errors", [])]
    open_prs = branch.get("open_prs", [])
    merged_prs = branch.get("merged_prs", [])
    ahead = branch.get("ahead_by")
    protected = is_protected(name, branch, default_branch, policy)
    committed_at = parse_time(branch.get("head_committed_at"))
    age_days = None
    if committed_at is not None:
        age_days = max(0, int((generated_at - committed_at).total_seconds() // 86400))

    evidence = {
        "protected": protected,
        "open_pr_count": len(open_prs),
        "merged_pr_count": len(merged_prs),
        "closed_unmerged_pr_count": len(branch.get("closed_unmerged_prs", [])),
        "ahead_by": ahead,
        "behind_by": branch.get("behind_by"),
        "compare_status": branch.get("compare_status"),
        "age_days": age_days,
        "evidence_errors": evidence_errors,
    }

    if protected:
        return decision(name, "PROTECTED", "KEEP", 0, "reserved or protected branch", evidence)
    if open_prs:
        return decision(name, "ACTIVE", "KEEP", 0, "open pull request proves active review", evidence)
    if evidence_errors and policy.get("fail_closed_on_evidence_error", True):
        return decision(name, "UNKNOWN_BLOCKED", "BLOCK", 0, "incomplete evidence fails closed", evidence)
    if merged_prs:
        return decision(name, "MERGED_REDUNDANT", "DELETE", 100, "merged pull request proves lifecycle completion", evidence)
    if ahead == 0:
        return decision(name, "REACHABLE_REDUNDANT", "DELETE", 98, "branch contributes zero commits ahead of default", evidence)
    if isinstance(ahead, int) and ahead > 0:
        if age_days is not None and age_days >= int(policy["stale_days"]):
            return decision(name, "STALE_REVIEW", "REVIEW_CONSOLIDATE", 0, "old branch still contains unique commits", evidence)
        return decision(name, "DIVERGENT_PRESERVE", "KEEP", 0, "unique commits require preservation", evidence)
    return decision(name, "UNKNOWN_BLOCKED", "BLOCK", 0, "comparison evidence is insufficient", evidence)

def decision(name: str, state: str, action: str, confidence: int, reason: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "branch": name,
        "state": state,
        "action": action,
        "cleanup_confidence": confidence,
        "reason": reason,
        "evidence": evidence,
    }

def family_rank(item: dict[str, Any], original: dict[str, Any]) -> tuple[Any, ...]:
    state = item["state"]
    priority = {
        "ACTIVE": 6,
        "DIVERGENT_PRESERVE": 5,
        "STALE_REVIEW": 4,
        "PROTECTED": 3,
        "MERGED_REDUNDANT": 2,
        "REACHABLE_REDUNDANT": 1,
        "UNKNOWN_BLOCKED": 0,
    }.get(state, 0)
    ahead = original.get("ahead_by")
    ahead_score = ahead if isinstance(ahead, int) else -1
    committed = parse_time(original.get("head_committed_at"))
    timestamp = committed.timestamp() if committed else 0
    return (priority, ahead_score, timestamp, item["branch"])

def build_plan(inventory: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    errors = validate_inventory(inventory)
    if errors:
        raise ValueError("; ".join(errors))
    generated_at = parse_time(inventory["generated_at"])
    assert generated_at is not None
    default_branch = inventory["default_branch"]
    originals = {branch["name"]: branch for branch in inventory["branches"]}

    decisions = [
        classify(branch, default_branch=default_branch, generated_at=generated_at, policy=policy)
        for branch in inventory["branches"]
    ]
    for item in decisions:
        item["family"] = family_key(item["branch"], policy)
        if (
            item["action"] == "DELETE"
            and (
                item["state"] not in set(policy["automatic_delete_states"])
                or item["cleanup_confidence"] < int(policy["minimum_delete_confidence"])
            )
        ):
            item["action"] = "BLOCK"
            item["reason"] = "delete candidate does not satisfy automatic cleanup policy"

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in decisions:
        grouped[item["family"]].append(item)

    families: list[dict[str, Any]] = []
    for key, members in sorted(grouped.items()):
        if len(members) < 2:
            continue
        ranked = sorted(
            members,
            key=lambda item: family_rank(item, originals[item["branch"]]),
            reverse=True,
        )
        lead = ranked[0]
        divergent = [
            m["branch"] for m in ranked
            if m["state"] in {"ACTIVE", "DIVERGENT_PRESERVE", "STALE_REVIEW"}
        ]
        families.append(
            {
                "family": key,
                "lead": lead["branch"],
                "members": [m["branch"] for m in ranked],
                "divergent_members": divergent,
                "consolidation_recommended": len(divergent) > 1,
                "note": (
                    "Review unique siblings for synthesis into the family lead; naming is not equivalence proof."
                    if len(divergent) > 1
                    else "Family grouping is informational; redundant members may follow their individual cleanup action."
                ),
            }
        )

    counts = Counter(item["state"] for item in decisions)
    action_counts = Counter(item["action"] for item in decisions)
    inventory_digest = sha256(inventory)
    plan_core = {
        "schema": SCHEMA,
        "repository": inventory["repository"],
        "default_branch": default_branch,
        "generated_at": inventory["generated_at"],
        "policy_version": policy["version"],
        "inventory_sha256": inventory_digest,
        "classifications": dict(sorted(counts.items())),
        "actions": dict(sorted(action_counts.items())),
        "branches": sorted(decisions, key=lambda x: x["branch"]),
        "families": families,
    }
    plan_core["plan_sha256"] = sha256(plan_core)
    return plan_core

def cmd_validate(args: argparse.Namespace) -> int:
    payload = load_json(args.snapshot)
    errors = validate_inventory(payload)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        return 2
    print(json.dumps({"ok": True, "branches": len(payload["branches"])}, indent=2))
    return 0

def cmd_plan(args: argparse.Namespace) -> int:
    inventory = load_json(args.snapshot)
    policy = load_policy(args.policy)
    plan = build_plan(inventory, policy)
    rendered = json.dumps(plan, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0

def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="branch-lifecycle-intelligence")
    sub = root.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("snapshot", type=Path)
    validate.set_defaults(func=cmd_validate)
    plan = sub.add_parser("plan")
    plan.add_argument("snapshot", type=Path)
    plan.add_argument("--policy", type=Path)
    plan.add_argument("--output", type=Path)
    plan.set_defaults(func=cmd_plan)
    return root

def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
