#!/usr/bin/env python3
"""Fail-closed SDK mission acceptance gate; no external side effects."""
import json
import sys
from pathlib import Path

REQUIRED = (
    "recovery", "implementation", "integration", "real_execution",
    "tests", "build", "typecheck", "imports", "error_paths",
    "defect_regression", "revision_readback", "durable_receipts", "reproduction",
)
STATES = {"OPEN", "RUNNING", "BLOCKED", "FAILED", "VERIFIED", "COMPLETE"}


def verified_readback(value, revision):
    """Reject booleans and readbacks detached from the tested source revision."""
    return (
        isinstance(value, dict)
        and value.get("status") == "confirmed"
        and value.get("revision") == revision
        and value.get("source") == "provider"
        and isinstance(value.get("receipt_id"), str)
        and len(value["receipt_id"]) >= 8
        and isinstance(value.get("observed_at"), str)
        and bool(value["observed_at"])
    )


def decide(m):
    errors = []
    if m.get("state") not in STATES:
        errors.append("INVALID_STATE")
    elif m["state"] not in {"VERIFIED", "COMPLETE"}:
        errors.append("NON_TERMINAL_STATE")
    revision = m.get("revision")
    if not isinstance(revision, str) or len(revision) < 12:
        errors.append("MISSING_REVISION")
    criteria = m.get("criteria")
    if not isinstance(criteria, dict):
        criteria = {}
    for key in REQUIRED:
        e = criteria.get(key)
        if (
            not isinstance(e, dict)
            or e.get("status") != "passed"
            or not e.get("evidence")
            or e.get("revision") != revision
        ):
            errors.append("UNVERIFIED:" + key)
        elif e.get("kind") in ("mock", "static", "planned") and key in (
            "integration", "real_execution", "error_paths"
        ):
            errors.append("NON_OPERATIONAL_EVIDENCE:" + key)
    if m.get("outstanding_actions"):
        errors.append("OUTSTANDING_ACTIONS")
    if m.get("unresolved_defects"):
        errors.append("UNRESOLVED_DEFECTS")
    if m.get("interrupted"):
        errors.append("INTERRUPTED")
    if m.get("ambiguous_mutation"):
        errors.append("AMBIGUOUS_MUTATION")
    if m.get("ci") != "passed":
        errors.append("CI_NOT_PASSED")
    if m.get("deployed") and not verified_readback(m.get("deployment_readback"), revision):
        errors.append("DEPLOYMENT_UNVERIFIED")
    if m.get("provider_mutation") and not verified_readback(m.get("provider_readback"), revision):
        errors.append("PROVIDER_UNVERIFIED")
    if m.get("claims_complete") and m.get("draft_only"):
        errors.append("DRAFT_NOT_DEPLOYED")
    return {
        "decision": "COMPLETE" if not errors else (
            "BLOCKED" if m.get("state") == "BLOCKED" else "OPEN"
        ),
        "accepted": not errors,
        "reasons": errors,
        "revision": revision,
    }


if __name__ == "__main__":
    result = decide(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["accepted"] else 1)
