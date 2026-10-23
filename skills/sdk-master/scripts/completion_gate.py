#!/usr/bin/env python3
"""Fail-closed, revision-bound SDK mission acceptance. Never runs external actions.

Receipt hashes verify local evidence integrity, not remote provider truth. Provider-native
readback still must be independently performed and recorded before a real-world claim.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

REQUIRED = (
    "recovery", "implementation", "integration", "real_execution", "tests", "build",
    "typecheck", "imports", "error_paths", "defect_regression", "revision_readback",
    "durable_receipts", "reproduction",
)
STATES = {"OPEN", "RUNNING", "BLOCKED", "FAILED", "VERIFIED", "COMPLETE"}
OPERATIONAL = {"integration", "real_execution", "error_paths"}
NON_OPERATIONAL = {"mock", "static", "planned", "fixture", "synthetic"}
SHA = re.compile(r"[a-f0-9]{64}\Z")
REVISION = re.compile(r"[a-f0-9]{40}\Z")


def check_receipt(evidence, criterion, revision, kind, receipt_root):
    """Verify the referenced receipt is a safe, unchanged, bound JSON file."""
    if not isinstance(evidence, dict) or not receipt_root:
        return "MISSING_VERIFIABLE_RECEIPT"
    relative, claimed_hash = evidence.get("path"), evidence.get("sha256")
    if not isinstance(relative, str) or not isinstance(claimed_hash, str) or not SHA.fullmatch(claimed_hash):
        return "INVALID_RECEIPT_REFERENCE"
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix != ".json" or not relative.startswith("evidence/"):
        return "UNSAFE_RECEIPT_PATH"
    try:
        root = Path(receipt_root).resolve(strict=True)
        path = root.joinpath(rel)
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
            return "UNSAFE_RECEIPT_PATH"
        blob = path.read_bytes()
        if len(blob) > 1_000_000:
            return "RECEIPT_OVERSIZE"
        if hashlib.sha256(blob).hexdigest() != claimed_hash:
            return "RECEIPT_HASH_MISMATCH"
        body = json.loads(blob)
        if not isinstance(body, dict):
            return "INVALID_RECEIPT_BODY"
        if (body.get("criterion"), body.get("revision"), body.get("status"), body.get("kind")) != (criterion, revision, "passed", kind):
            return "RECEIPT_BINDING_MISMATCH"
        if not all(isinstance(body.get(x), str) and body[x].strip() for x in ("executor", "run_id", "finished_at", "command")):
            return "RECEIPT_PROVENANCE_MISSING"
        if body.get("exit_code") != 0:
            return "RECEIPT_EXECUTION_UNVERIFIED"
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return "RECEIPT_UNREADABLE"
    return None


def decide(m, receipt_root=None):
    errors = []
    if not isinstance(m, dict):
        return {"decision": "OPEN", "accepted": False, "reasons": ["INVALID_MISSION"], "revision": None}
    state = m.get("state")
    if state not in STATES:
        errors.append("INVALID_STATE")
    elif state not in {"VERIFIED", "COMPLETE"}:
        errors.append("MISSION_NOT_VERIFIED")
    revision = m.get("revision")
    if not isinstance(revision, str) or not REVISION.fullmatch(revision):
        errors.append("INVALID_REVISION")
    criteria = m.get("criteria")
    if not isinstance(criteria, dict):
        criteria = {}
    for key in REQUIRED:
        entry = criteria.get(key)
        if not isinstance(entry, dict) or entry.get("status") != "passed" or entry.get("revision") != revision:
            errors.append("UNVERIFIED:" + key)
            continue
        kind = entry.get("kind")
        if kind in NON_OPERATIONAL and key in OPERATIONAL:
            errors.append("NON_OPERATIONAL_EVIDENCE:" + key)
        receipt_error = check_receipt(entry.get("evidence"), key, revision, kind, receipt_root)
        if receipt_error:
            errors.append(receipt_error + ":" + key)
    for field, error in (("outstanding_actions", "OUTSTANDING_ACTIONS"), ("unresolved_defects", "UNRESOLVED_DEFECTS")):
        if m.get(field):
            errors.append(error)
    for field, error in (("interrupted", "INTERRUPTED"), ("ambiguous_mutation", "AMBIGUOUS_MUTATION")):
        if m.get(field):
            errors.append(error)
    if m.get("ci") != "passed":
        errors.append("CI_NOT_PASSED")
    if m.get("deployed") and not m.get("deployment_readback"):
        errors.append("DEPLOYMENT_UNVERIFIED")
    if m.get("provider_mutation") and not m.get("provider_readback"):
        errors.append("PROVIDER_UNVERIFIED")
    if m.get("claims_complete") and m.get("draft_only"):
        errors.append("DRAFT_NOT_DEPLOYED")
    return {"decision": "COMPLETE" if not errors else ("BLOCKED" if state == "BLOCKED" else "OPEN"),
            "accepted": not errors, "reasons": errors, "revision": revision}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: completion_gate.py <MISSION_STATE.json>", file=sys.stderr)
        sys.exit(2)
    mission_path = Path(sys.argv[1])
    result = decide(json.loads(mission_path.read_text()), receipt_root=mission_path.parent)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["accepted"] else 1)
