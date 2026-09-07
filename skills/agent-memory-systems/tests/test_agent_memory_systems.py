#!/usr/bin/env python3
"""Behavioral tests for durable continuation and hydration semantics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from continuity import (
    ContinuityError,
    add_contradiction,
    add_peer,
    add_source,
    hydration_packet,
    load_projection,
    mark_complete,
    new_projection,
    record_transition,
    resolve_question,
    save_projection,
    set_next_action,
    validate_projection,
)


def _state():
    return new_projection(
        mission_id="mission-1",
        operator_intent="Continue existing work without reconstruction.",
        active_target="Advance from the nearest valid continuation point.",
    )


def _persist(path: Path, state):
    prior = state.get("state_digest")
    save_projection(path, state, previous_digest=prior)
    return load_projection(path)


def test_new_projection_is_integrity_bound_and_hydratable():
    state = _state()
    validate_projection(state)
    packet = hydration_packet(state)

    assert packet["projection_id"] == state["projection_id"]
    assert packet["state_digest"] == state["state_digest"]
    assert packet["last_verified_state"] == "projection initialized"
    assert "route retrieval" in packet["boot_rule"]
    assert packet["next_action"]["action"]


def test_verified_transition_requires_source_backed_evidence(tmp_path: Path):
    state = _state()
    with pytest.raises(ContinuityError, match="evidence_refs"):
        record_transition(
            state,
            action="Build feature",
            observed_result="Feature changed",
            after_state="feature complete",
            evidence_refs=[],
        )

    src = add_source(
        state,
        provider="github",
        locator="GlacierEQ/mega-skills@abc123",
        scope="implementation and test result",
        truth_state="behavior_verified",
        source_id="src-github",
    )

    receipt = record_transition(
        state,
        action="Build feature",
        observed_result="Tests passed against the implementation.",
        after_state="feature behavior verified",
        evidence_refs=[src],
        next_action={
            "action": "Integrate the verified feature.",
            "why": "Implementation is complete; integration is the next dependency.",
            "requires_authority": False,
            "blocked_by": [],
            "critical_path": ["integrate", "verify integration"],
        },
    )

    persisted = _persist(tmp_path / "continuation.json", state)
    assert receipt.startswith("rcpt-")
    assert persisted["continuation"]["last_verified_state"] == "feature behavior verified"
    assert persisted["continuation"]["critical_path"] == ["integrate", "verify integration"]


def test_dirty_projection_cannot_be_hydrated_as_durable_state():
    state = _state()
    add_source(
        state,
        provider="github",
        locator="GlacierEQ/mega-skills@abc123",
        scope="implementation",
        truth_state="inspected",
    )
    with pytest.raises(ContinuityError, match="state_digest"):
        hydration_packet(state)


def test_resolved_question_cannot_silently_reopen_or_be_replaced(tmp_path: Path):
    state = _state()
    src = add_source(
        state,
        provider="dropbox",
        locator="/case/evidence/receipt.pdf",
        scope="receipt identity",
        truth_state="externally_verified",
        source_id="src-receipt",
    )
    resolve_question(
        state,
        question_id="q-receipt",
        question="Was the native receipt recovered?",
        resolution="Yes. Native receipt recovered and verified.",
        evidence_refs=[src],
        reopen_conditions=["new contradictory evidence", "source becomes unavailable"],
    )

    with pytest.raises(ContinuityError, match="already resolved"):
        resolve_question(
            state,
            question_id="q-receipt",
            question="Was the native receipt recovered?",
            resolution="Unknown",
            evidence_refs=[src],
        )

    persisted = _persist(tmp_path / "continuation.json", state)
    packet = hydration_packet(persisted)
    assert packet["resolved_questions"][0]["resolution"].startswith("Yes.")


def test_contradictions_and_peer_projections_survive_hydration(tmp_path: Path):
    state = _state()
    a = add_source(
        state,
        provider="provider-a",
        locator="resource-a",
        scope="routing state",
        truth_state="externally_verified",
        source_id="src-a",
    )
    b = add_source(
        state,
        provider="provider-b",
        locator="resource-b",
        scope="routing state",
        truth_state="externally_verified",
        source_id="src-b",
    )
    add_contradiction(
        state,
        contradiction_id="ctr-routing",
        claim_a="Provider A says delivered.",
        claim_b="Provider B says not received.",
        evidence_refs=[a, b],
    )
    add_peer(
        state,
        provider="supabase",
        locator="project://case-control-plane/continuation",
        relationship="peer",
        revision="42",
    )
    add_peer(
        state,
        provider="github",
        locator="GlacierEQ/case-control-plane@deadbeef",
        relationship="projection",
    )

    persisted = _persist(tmp_path / "continuation.json", state)
    packet = hydration_packet(persisted)
    assert packet["open_contradictions"][0]["id"] == "ctr-routing"
    assert len(packet["peer_projections"]) == 2
    assert {p["provider"] for p in packet["peer_projections"]} == {"supabase", "github"}


def test_persistence_is_atomic_and_links_previous_digest(tmp_path: Path):
    path = tmp_path / "continuation.json"
    state = _state()
    first = save_projection(path, state)

    loaded = load_projection(path)
    assert loaded["state_digest"] == first

    set_next_action(
        loaded,
        action="Run integration test.",
        why="Unit behavior is already verified.",
        critical_path=["integration test", "readback"],
    )
    second = save_projection(path, loaded, previous_digest=first)

    reloaded = load_projection(path)
    assert second != first
    assert reloaded["lineage"]["previous_digest"] == first
    assert reloaded["state_digest"] == second


def test_tampering_is_detected(tmp_path: Path):
    path = tmp_path / "continuation.json"
    state = _state()
    save_projection(path, state)

    raw = json.loads(path.read_text())
    raw["mission"]["active_target"] = "silently changed target"
    path.write_text(json.dumps(raw))

    with pytest.raises(ContinuityError, match="state_digest"):
        load_projection(path)


def test_complete_mission_has_no_execution_tail(tmp_path: Path):
    state = _state()
    src = add_source(
        state,
        provider="ci",
        locator="build://123",
        scope="completion verification",
        truth_state="behavior_verified",
        source_id="src-ci",
    )
    mark_complete(
        state,
        final_state="requested outcome verified complete",
        evidence_refs=[src],
    )
    persisted = _persist(tmp_path / "continuation.json", state)
    validate_projection(persisted)

    packet = hydration_packet(persisted)
    assert packet["mission"]["status"] == "complete"
    assert packet["next_action"] is None
    assert packet["critical_path"] == []
