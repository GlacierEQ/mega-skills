from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

SCHEMA_VERSION = "2.0.0"
TRUTH_STATES = {
    "operator_observation",
    "externally_verified",
    "behavior_verified",
    "measured",
    "inspected",
    "implemented",
    "inference",
    "hypothesis",
    "unknown",
    "blocked",
}
MISSION_STATUSES = {"active", "blocked", "complete"}
RELATIONSHIPS = {
    "peer",
    "projection",
    "derived_from",
    "supersedes",
    "superseded_by",
    "corroborates",
    "contradicts",
}
CONTRADICTION_STATUSES = {"open", "resolved"}
BLOCKER_STATUSES = {"open", "resolved"}

class ContinuityError(ValueError):
    """Raised when continuation state violates a behavioral contract."""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _payload_for_digest(state: Mapping[str, Any]) -> dict[str, Any]:
    payload = deepcopy(dict(state))
    payload.pop("state_digest", None)
    return payload

def compute_digest(state: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(_payload_for_digest(state))).hexdigest()

def verify_digest(state: Mapping[str, Any]) -> bool:
    digest = state.get("state_digest")
    return isinstance(digest, str) and digest == compute_digest(state)

def _require_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContinuityError(f"{name} must be a non-empty string")
    return value

def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContinuityError(f"{name} must be a list")
    return value

def _unique_ids(items: Iterable[Mapping[str, Any]], field: str, section: str) -> None:
    seen: set[str] = set()
    for item in items:
        value = _require_str(item.get(field), f"{section}.{field}")
        if value in seen:
            raise ContinuityError(f"duplicate {section}.{field}: {value}")
        seen.add(value)

def new_projection(
    *,
    mission_id: str,
    operator_intent: str,
    active_target: str,
    projection_id: str | None = None,
    next_action: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    mission_id = _require_str(mission_id, "mission_id")
    operator_intent = _require_str(operator_intent, "operator_intent")
    active_target = _require_str(active_target, "active_target")
    now = utc_now()
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "projection_id": projection_id or str(uuid.uuid4()),
        "mission": {
            "mission_id": mission_id,
            "operator_intent": operator_intent,
            "active_target": active_target,
            "status": "active",
            "scope": [],
        },
        "continuation": {
            "last_verified_state": "projection initialized",
            "critical_path": [],
            "next_action": dict(next_action) if next_action is not None else {
                "action": "Acquire the minimum source-bearing state required to determine the next material dependency.",
                "why": "Boot context routes retrieval; it does not replace hydration.",
                "requires_authority": False,
                "blocked_by": [],
            },
            "completed": [],
            "blockers": [],
            "resolved_questions": [],
        },
        "sources": [],
        "contradictions": [],
        "receipts": [],
        "peers": [],
        "lineage": {
            "previous_digest": None,
            "created_at": now,
        },
        "updated_at": now,
    }
    state["state_digest"] = compute_digest(state)
    validate_projection(state)
    return state

def validate_projection(state: Mapping[str, Any], *, verify_integrity: bool = True) -> None:
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ContinuityError(
            f"schema_version must be {SCHEMA_VERSION!r}; got {state.get('schema_version')!r}"
        )
    _require_str(state.get("projection_id"), "projection_id")

    mission = state.get("mission")
    if not isinstance(mission, Mapping):
        raise ContinuityError("mission must be an object")
    _require_str(mission.get("mission_id"), "mission.mission_id")
    _require_str(mission.get("operator_intent"), "mission.operator_intent")
    _require_str(mission.get("active_target"), "mission.active_target")
    status = mission.get("status")
    if status not in MISSION_STATUSES:
        raise ContinuityError(f"mission.status must be one of {sorted(MISSION_STATUSES)}")
    _require_list(mission.get("scope", []), "mission.scope")

    continuation = state.get("continuation")
    if not isinstance(continuation, Mapping):
        raise ContinuityError("continuation must be an object")
    _require_str(continuation.get("last_verified_state"), "continuation.last_verified_state")
    _require_list(continuation.get("critical_path"), "continuation.critical_path")
    completed = _require_list(continuation.get("completed"), "continuation.completed")
    blockers = _require_list(continuation.get("blockers"), "continuation.blockers")
    resolved = _require_list(
        continuation.get("resolved_questions"), "continuation.resolved_questions"
    )
    _unique_ids(completed, "id", "continuation.completed")
    _unique_ids(blockers, "id", "continuation.blockers")
    _unique_ids(resolved, "id", "continuation.resolved_questions")

    next_action = continuation.get("next_action")
    if status == "complete":
        if next_action not in (None, {}):
            raise ContinuityError("completed missions must not carry an executable next_action")
    else:
        if not isinstance(next_action, Mapping):
            raise ContinuityError("active/blocked missions require continuation.next_action")
        _require_str(next_action.get("action"), "continuation.next_action.action")
        _require_str(next_action.get("why"), "continuation.next_action.why")
        if not isinstance(next_action.get("requires_authority"), bool):
            raise ContinuityError("continuation.next_action.requires_authority must be boolean")
        _require_list(next_action.get("blocked_by"), "continuation.next_action.blocked_by")

    sources = _require_list(state.get("sources"), "sources")
    _unique_ids(sources, "source_id", "sources")
    for source in sources:
        _require_str(source.get("provider"), "sources.provider")
        _require_str(source.get("locator"), "sources.locator")
        _require_str(source.get("observed_at"), "sources.observed_at")
        _require_str(source.get("scope"), "sources.scope")
        truth_state = source.get("truth_state")
        if truth_state not in TRUTH_STATES:
            raise ContinuityError(f"invalid sources.truth_state: {truth_state!r}")

    contradictions = _require_list(state.get("contradictions"), "contradictions")
    _unique_ids(contradictions, "id", "contradictions")
    for contradiction in contradictions:
        _require_str(contradiction.get("claim_a"), "contradictions.claim_a")
        _require_str(contradiction.get("claim_b"), "contradictions.claim_b")
        if contradiction.get("status") not in CONTRADICTION_STATUSES:
            raise ContinuityError("contradictions.status must be open or resolved")
        _require_list(contradiction.get("evidence_refs", []), "contradictions.evidence_refs")

    receipts = _require_list(state.get("receipts"), "receipts")
    _unique_ids(receipts, "receipt_id", "receipts")
    source_ids = {s["source_id"] for s in sources}
    for receipt in receipts:
        _require_str(receipt.get("action"), "receipts.action")
        _require_str(receipt.get("before_state"), "receipts.before_state")
        _require_str(receipt.get("observed_result"), "receipts.observed_result")
        _require_str(receipt.get("after_state"), "receipts.after_state")
        evidence_refs = _require_list(receipt.get("evidence_refs"), "receipts.evidence_refs")
        if not evidence_refs:
            raise ContinuityError("material transition receipts require evidence_refs")
        missing = [ref for ref in evidence_refs if ref not in source_ids]
        if missing:
            raise ContinuityError(f"receipt references unknown source ids: {missing}")
        _require_str(receipt.get("verified_at"), "receipts.verified_at")

    peers = _require_list(state.get("peers"), "peers")
    for peer in peers:
        _require_str(peer.get("provider"), "peers.provider")
        _require_str(peer.get("locator"), "peers.locator")
        if peer.get("relationship") not in RELATIONSHIPS:
            raise ContinuityError(f"invalid peers.relationship: {peer.get('relationship')!r}")

    lineage = state.get("lineage")
    if not isinstance(lineage, Mapping):
        raise ContinuityError("lineage must be an object")
    previous_digest = lineage.get("previous_digest")
    if previous_digest is not None and (
        not isinstance(previous_digest, str) or len(previous_digest) != 64
    ):
        raise ContinuityError("lineage.previous_digest must be null or a sha256 hex digest")
    _require_str(lineage.get("created_at"), "lineage.created_at")
    _require_str(state.get("updated_at"), "updated_at")

    if verify_integrity and not verify_digest(state):
        raise ContinuityError("state_digest does not match current projection content")

def load_projection(path: str | os.PathLike[str], *, verify_integrity: bool = True) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    validate_projection(state, verify_integrity=verify_integrity)
    return state

def save_projection(
    path: str | os.PathLike[str],
    state: MutableMapping[str, Any],
    *,
    previous_digest: str | None = None,
) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if previous_digest is None and target.exists():
        prior = load_projection(target)
        previous_digest = prior["state_digest"]

    state["updated_at"] = utc_now()
    lineage = state.setdefault("lineage", {})
    lineage.setdefault("created_at", state["updated_at"])
    lineage["previous_digest"] = previous_digest
    state["state_digest"] = compute_digest(state)
    validate_projection(state)

    encoded = json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, target)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    return state["state_digest"]

def add_source(
    state: MutableMapping[str, Any],
    *,
    provider: str,
    locator: str,
    scope: str,
    truth_state: str,
    revision: str | None = None,
    content_hash: str | None = None,
    observed_at: str | None = None,
    source_id: str | None = None,
) -> str:
    if truth_state not in TRUTH_STATES:
        raise ContinuityError(f"invalid truth_state {truth_state!r}")
    source_id = source_id or f"src-{uuid.uuid4().hex[:12]}"
    source = {
        "source_id": source_id,
        "provider": _require_str(provider, "provider"),
        "locator": _require_str(locator, "locator"),
        "scope": _require_str(scope, "scope"),
        "truth_state": truth_state,
        "observed_at": observed_at or utc_now(),
    }
    if revision:
        source["revision"] = revision
    if content_hash:
        source["content_hash"] = content_hash
    state["sources"].append(source)
    return source_id

def add_peer(
    state: MutableMapping[str, Any],
    *,
    provider: str,
    locator: str,
    relationship: str = "peer",
    revision: str | None = None,
) -> None:
    if relationship not in RELATIONSHIPS:
        raise ContinuityError(f"invalid relationship {relationship!r}")
    peer = {
        "provider": _require_str(provider, "provider"),
        "locator": _require_str(locator, "locator"),
        "relationship": relationship,
    }
    if revision:
        peer["revision"] = revision
    state["peers"].append(peer)

def add_contradiction(
    state: MutableMapping[str, Any],
    *,
    claim_a: str,
    claim_b: str,
    evidence_refs: Iterable[str] = (),
    contradiction_id: str | None = None,
) -> str:
    contradiction_id = contradiction_id or f"ctr-{uuid.uuid4().hex[:12]}"
    state["contradictions"].append({
        "id": contradiction_id,
        "claim_a": _require_str(claim_a, "claim_a"),
        "claim_b": _require_str(claim_b, "claim_b"),
        "status": "open",
        "resolution": None,
        "evidence_refs": list(evidence_refs),
        "created_at": utc_now(),
    })
    return contradiction_id

def resolve_question(
    state: MutableMapping[str, Any],
    *,
    question_id: str,
    question: str,
    resolution: str,
    evidence_refs: Iterable[str],
    reopen_conditions: Iterable[str] = (),
) -> None:
    existing = {item["id"] for item in state["continuation"]["resolved_questions"]}
    if question_id in existing:
        raise ContinuityError(
            f"question {question_id!r} is already resolved; use an explicit reopen operation before replacing it"
        )
    refs = list(evidence_refs)
    if not refs:
        raise ContinuityError("resolved questions require at least one evidence reference")
    state["continuation"]["resolved_questions"].append({
        "id": _require_str(question_id, "question_id"),
        "question": _require_str(question, "question"),
        "resolution": _require_str(resolution, "resolution"),
        "evidence_refs": refs,
        "resolved_at": utc_now(),
        "reopen_conditions": list(reopen_conditions),
    })

def reopen_question(
    state: MutableMapping[str, Any],
    *,
    question_id: str,
    reason: str,
) -> dict[str, Any]:
    resolved = state["continuation"]["resolved_questions"]
    for index, item in enumerate(resolved):
        if item["id"] == question_id:
            reopened = resolved.pop(index)
            reopened["reopened_at"] = utc_now()
            reopened["reopen_reason"] = _require_str(reason, "reason")
            state.setdefault("reopened_questions", []).append(reopened)
            return reopened
    raise ContinuityError(f"resolved question not found: {question_id}")

def set_next_action(
    state: MutableMapping[str, Any],
    *,
    action: str,
    why: str,
    requires_authority: bool = False,
    blocked_by: Iterable[str] = (),
    critical_path: Iterable[str] | None = None,
) -> None:
    if state["mission"]["status"] == "complete":
        raise ContinuityError("cannot set next_action on a completed mission")
    state["continuation"]["next_action"] = {
        "action": _require_str(action, "action"),
        "why": _require_str(why, "why"),
        "requires_authority": bool(requires_authority),
        "blocked_by": list(blocked_by),
    }
    if critical_path is not None:
        state["continuation"]["critical_path"] = list(critical_path)

def record_transition(
    state: MutableMapping[str, Any],
    *,
    action: str,
    observed_result: str,
    after_state: str,
    evidence_refs: Iterable[str],
    completed_description: str | None = None,
    next_action: Mapping[str, Any] | None = None,
) -> str:
    before_state = state["continuation"]["last_verified_state"]
    refs = list(evidence_refs)
    if not refs:
        raise ContinuityError("verified transitions require evidence_refs")
    known = {source["source_id"] for source in state["sources"]}
    missing = [ref for ref in refs if ref not in known]
    if missing:
        raise ContinuityError(f"transition references unknown source ids: {missing}")

    receipt_id = f"rcpt-{uuid.uuid4().hex[:12]}"
    state["receipts"].append({
        "receipt_id": receipt_id,
        "action": _require_str(action, "action"),
        "before_state": _require_str(before_state, "before_state"),
        "observed_result": _require_str(observed_result, "observed_result"),
        "after_state": _require_str(after_state, "after_state"),
        "evidence_refs": refs,
        "verified_at": utc_now(),
    })
    state["continuation"]["last_verified_state"] = after_state

    if completed_description:
        state["continuation"]["completed"].append({
            "id": f"done-{uuid.uuid4().hex[:12]}",
            "description": _require_str(completed_description, "completed_description"),
            "receipt_id": receipt_id,
            "verified_at": utc_now(),
        })

    if next_action is not None:
        set_next_action(
            state,
            action=next_action["action"],
            why=next_action["why"],
            requires_authority=bool(next_action.get("requires_authority", False)),
            blocked_by=next_action.get("blocked_by", []),
            critical_path=next_action.get("critical_path"),
        )
    return receipt_id

def mark_complete(
    state: MutableMapping[str, Any],
    *,
    final_state: str,
    evidence_refs: Iterable[str],
) -> str:
    receipt_id = record_transition(
        state,
        action="Mark mission complete",
        observed_result="Completion criteria satisfied and verified.",
        after_state=final_state,
        evidence_refs=evidence_refs,
        completed_description="Mission completion verified",
    )
    state["mission"]["status"] = "complete"
    state["continuation"]["next_action"] = None
    state["continuation"]["critical_path"] = []
    return receipt_id

def hydration_packet(state: Mapping[str, Any]) -> dict[str, Any]:
    validate_projection(state)
    continuation = state["continuation"]
    open_blockers = [
        deepcopy(item)
        for item in continuation["blockers"]
        if item.get("status", "open") == "open"
    ]
    open_contradictions = [
        deepcopy(item)
        for item in state["contradictions"]
        if item.get("status") == "open"
    ]
    return {
        "schema_version": state["schema_version"],
        "projection_id": state["projection_id"],
        "state_digest": state["state_digest"],
        "mission": deepcopy(state["mission"]),
        "last_verified_state": continuation["last_verified_state"],
        "critical_path": deepcopy(continuation["critical_path"]),
        "next_action": deepcopy(continuation["next_action"]),
        "open_blockers": open_blockers,
        "resolved_questions": deepcopy(continuation["resolved_questions"]),
        "open_contradictions": open_contradictions,
        "source_pointers": deepcopy(state["sources"]),
        "peer_projections": deepcopy(state["peers"]),
        "transition_receipts": deepcopy(state["receipts"][-10:]),
        "updated_at": state["updated_at"],
        "boot_rule": (
            "Use this packet to route retrieval and resume from the last verified state. "
            "Do not treat the packet as a substitute for materially required live/source-bearing hydration."
        ),
    }
