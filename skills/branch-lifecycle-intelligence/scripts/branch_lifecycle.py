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
ADMISSION_SCHEMA = "glaciereq.branch-admission-request.v1"
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


def validate_admission_request(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != ADMISSION_SCHEMA:
        errors.append(f"schema must be {ADMISSION_SCHEMA}")
    for field in ("requested_branch", "workstream_id"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} is required")
    continuation = payload.get("continuation_of")
    if continuation is not None and (not isinstance(continuation, str) or not continuation.strip()):
        errors.append("continuation_of must be a non-empty string or null")
    bindings = payload.get("bindings", [])
    if not isinstance(bindings, list):
        errors.append("bindings must be an array")
    else:
        for index, row in enumerate(bindings):
            if not isinstance(row, dict):
                errors.append(f"bindings[{index}] must be an object")
                continue
            if not isinstance(row.get("workstream_id"), str) or not row["workstream_id"].strip():
                errors.append(f"bindings[{index}].workstream_id is required")
            if not isinstance(row.get("branch"), str) or not row["branch"].strip():
                errors.append(f"bindings[{index}].branch is required")
    return errors


def build_admission_decision(
    lifecycle_plan: dict[str, Any],
    request: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    errors = validate_admission_request(request)
    if errors:
        raise ValueError("; ".join(errors))
    if lifecycle_plan.get("schema") != SCHEMA:
        raise ValueError(f"lifecycle plan schema must be {SCHEMA}")

    rows = lifecycle_plan.get("branches")
    if not isinstance(rows, list):
        raise ValueError("lifecycle plan branches must be an array")
    by_branch = {
        row.get("branch"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("branch"), str)
    }

    requested = request["requested_branch"].strip()
    workstream_id = request["workstream_id"].strip()
    continuation = request.get("continuation_of")
    continuation = continuation.strip() if isinstance(continuation, str) else None
    bindings = [
        row
        for row in request.get("bindings", [])
        if row.get("workstream_id") == workstream_id and row.get("branch") in by_branch
    ]

    live_states = {"ACTIVE", "DIVERGENT_PRESERVE", "STALE_REVIEW"}
    closed_states = {"MERGED_REDUNDANT", "REACHABLE_REDUNDANT"}
    blocked_states = {"PROTECTED", "UNKNOWN_BLOCKED"}

    live_bound = [
        row["branch"]
        for row in bindings
        if by_branch[row["branch"]].get("state") in live_states
    ]
    closed_bound = [
        row["branch"]
        for row in bindings
        if by_branch[row["branch"]].get("state") in closed_states
    ]

    def emit(
        action: str,
        *,
        allow_create: bool,
        target_branch: str | None,
        reason: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        result = {
            "schema": "glaciereq.branch-admission-decision.v1",
            "repository": lifecycle_plan.get("repository"),
            "workstream_id": workstream_id,
            "requested_branch": requested,
            "action": action,
            "allow_create": allow_create,
            "target_branch": target_branch,
            "reason": reason,
            "evidence": evidence,
        }
        result["decision_sha256"] = sha256(result)
        return result

    if len(live_bound) > 1:
        return emit(
            "REVIEW_CONSOLIDATE",
            allow_create=False,
            target_branch=None,
            reason="multiple live branches are explicitly bound to the same workstream",
            evidence={
                "explicit_live_bindings": sorted(live_bound),
                "explicit_closed_bindings": sorted(closed_bound),
            },
        )

    if continuation:
        row = by_branch.get(continuation)
        if row is None:
            return emit(
                "BLOCK",
                allow_create=False,
                target_branch=None,
                reason="explicit continuation branch is not present in lifecycle evidence",
                evidence={"continuation_of": continuation},
            )
        state = row.get("state")
        if state in live_states:
            if live_bound and live_bound[0] != continuation:
                return emit(
                    "REVIEW_CONSOLIDATE",
                    allow_create=False,
                    target_branch=None,
                    reason="continuation request conflicts with the explicit live workstream binding",
                    evidence={
                        "continuation_of": continuation,
                        "explicit_live_binding": live_bound[0],
                    },
                )
            return emit(
                "REUSE_EXISTING",
                allow_create=False,
                target_branch=continuation,
                reason="explicit continuation points to a live branch in the same workstream",
                evidence={"continuation_state": state},
            )
        if state in closed_states:
            return emit(
                "CREATE_NEW",
                allow_create=True,
                target_branch=requested,
                reason="explicit continuation branch lifecycle is already closed",
                evidence={"continuation_of": continuation, "continuation_state": state},
            )
        if state in blocked_states:
            return emit(
                "BLOCK",
                allow_create=False,
                target_branch=None,
                reason="explicit continuation branch is protected or evidence-blocked",
                evidence={"continuation_of": continuation, "continuation_state": state},
            )

    if len(live_bound) == 1:
        target = live_bound[0]
        return emit(
            "REUSE_EXISTING",
            allow_create=False,
            target_branch=target,
            reason="exact workstream binding already has one live branch",
            evidence={
                "explicit_live_binding": target,
                "state": by_branch[target].get("state"),
            },
        )

    requested_family = family_key(requested, policy)
    family_collisions = sorted(
        row["branch"]
        for row in rows
        if isinstance(row, dict)
        and row.get("branch") != requested
        and row.get("state") in live_states
        and family_key(str(row.get("branch")), policy) == requested_family
    )
    if family_collisions:
        return emit(
            "CREATE_NEW_WITH_FAMILY_WARNING",
            allow_create=True,
            target_branch=requested,
            reason="similar live branch family exists, but naming alone is not semantic-equivalence proof",
            evidence={
                "family": requested_family,
                "similar_live_branches": family_collisions,
            },
        )

    return emit(
        "CREATE_NEW",
        allow_create=True,
        target_branch=requested,
        reason="no explicit live workstream binding or proven continuation exists",
        evidence={
            "explicit_closed_bindings": sorted(closed_bound),
            "family": requested_family,
        },
    )


def cmd_admit(args: argparse.Namespace) -> int:
    lifecycle_plan = load_json(args.plan)
    request = load_json(args.request)
    policy = load_policy(args.policy)
    decision_payload = build_admission_decision(lifecycle_plan, request, policy)
    rendered = json.dumps(decision_payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0

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
    admit = sub.add_parser("admit")
    admit.add_argument("plan", type=Path)
    admit.add_argument("request", type=Path)
    admit.add_argument("--policy", type=Path)
    admit.add_argument("--output", type=Path)
    admit.set_defaults(func=cmd_admit)
    return root

def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
