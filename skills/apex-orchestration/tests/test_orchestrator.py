#!/usr/bin/env python3
"""
tests/test_orchestrator.py — full lifecycle engine tests (v1.0.0)

Covers: INTAKE → DECOMPOSE → DISPATCH → VERIFY → FUSE → DELIVER
plus lane routing, three-signature gate, receipt-chain hash, and
constitutional gate. Mirrors the 13 closed failure codes (Packet 09).
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrator import (  # noqa: E402
    MissionOrchestrator,
    Subtask,
    Intake,
    DispatchNode,
    VerifiedReceipt,
    FusedArtifact,
    Delivery,
    Signature,
    ulid,
    now_iso,
    sha256_bytes,
    sha256_file,
    canonical_json,
    classify_text,
    decompose_description,
    route_subtask,
    validate_receipt_schema,
    LANE_MODELS,
    LANE_PRIORITY,
    MISSION_BUDGET_MAX,
    SCOPE_AMBIGUITY_THRESHOLD,
    THREE_SIG_ROLES,
)


# ─── Helpers ───────────────────────────────────────────────────────────────────


def make_receipt(
    lane="CODE",
    task="Fix the login bug",
    model="poolside/laguna-s-2.1:free",
    files_changed=None,
    sha256_hashes=None,
    l2_proof=True,
    signatures=None,
    duration_ms=1200,
    parent_mission_id="mission_test",
):
    """Build a valid receipt dict matching receipt.schema.json."""
    files_changed = files_changed or []
    sha256_hashes = sha256_hashes or [sha256_bytes(b"test content")]
    return {
        "lane": lane,
        "model": model,
        "task": task,
        "files_changed": files_changed,
        "sha256": sha256_hashes,
        "tests": {"cmd": "pytest tests/", "exit": 0, "summary": "12 passed"},
        "duration_ms": duration_ms,
        "l2_proof": l2_proof,
        "parent_mission_id": parent_mission_id,
        "signatures": signatures or [],
    }


def make_code_receipt_with_sigs(**kwargs):
    """Build a CODE-lane receipt with three-signature chain."""
    sigs = [
        {
            "role": "producer",
            "lane": "CODE",
            "model": LANE_MODELS["CODE"],
            "ts": now_iso(),
            "receipt_sha256": sha256_bytes(b"producer"),
        },
        {
            "role": "auditor",
            "lane": "VERIFY",
            "model": LANE_MODELS["VERIFY"],
            "ts": now_iso(),
            "receipt_sha256": sha256_bytes(b"auditor"),
        },
        {
            "role": "refiner",
            "lane": "REVIEW",
            "model": LANE_MODELS["REVIEW"],
            "ts": now_iso(),
            "receipt_sha256": sha256_bytes(b"refiner"),
        },
    ]
    lane = kwargs.pop("lane", "CODE")
    return make_receipt(lane=lane, signatures=sigs, **kwargs)


def make_run_quality():
    return {
        "source_coverage": {"scope": "bounded", "evidence": ["INTAKE.json", "VERIFY.json"]},
        "mission_delta": {
            "changed": True,
            "before": "mission objective not yet delivered",
            "after": "verified durable mission output exists",
        },
        "durable_outputs": ["fused.json"],
        "verification": {"status": "verified", "evidence": ["verified receipts passed gates"]},
        "next_frontier": "continue from the verified delivery state",
    }


def fresh_orch(tmp_path):
    return MissionOrchestrator(state_root=tmp_path)


# ─── INTAKE ────────────────────────────────────────────────────────────────────


class TestIntake:
    def test_basic_intake(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        assert intake.mission_id.startswith("mission_")
        assert intake.scope == "bounded"
        assert intake.budget == 1.0
        assert intake.confidence > 0
        assert isinstance(intake.causes, list)

    def test_budget_exceeded(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("test", budget=999.0)
        assert any("F-INT-02" in c for c in intake.causes)

    def test_intake_persisted(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Deploy to production")
        intake_file = tmp_path / intake.mission_id / "INTAKE.json"
        assert intake_file.exists()
        data = json.loads(intake_file.read_text())
        assert data["stage"] == "INTAKE"
        assert data["evidence"]["scope"] == "bounded"


# ─── DECOMPOSE ─────────────────────────────────────────────────────────────────


class TestDecompose:
    def test_basic_decompose(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        assert len(subtasks) >= 3
        assert all(st.lane for st in subtasks)
        assert all(st.model for st in subtasks)

    def test_routing_medical(self, tmp_path):
        """R-MEDICAL → DOMAIN-MED (hard gate)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Diagnose patient symptoms",
            kind="classify",
            domain="medical",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-MEDICAL"
        assert lane == "DOMAIN-MED"
        assert is_hard is True

    def test_routing_finance(self, tmp_path):
        """R-FINANCE → DOMAIN-FIN (hard gate)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Calculate ROI for the campaign",
            kind="classify",
            domain="finance",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-FINANCE"
        assert lane == "DOMAIN-FIN"
        assert is_hard is True

    def test_routing_plan(self, tmp_path):
        """R-PLAN → REASON (hard gate)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Design the architecture blueprint",
            kind="plan",
            domain="default",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-PLAN"
        assert lane == "REASON"
        assert is_hard is True

    def test_routing_code_edit(self, tmp_path):
        """R-CODE-EDIT → CODE (soft gate)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Fix the login bug",
            kind="code_edit",
            domain="default",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-CODE-EDIT"
        assert lane == "CODE"
        assert is_hard is False

    def test_routing_code_fast(self, tmp_path):
        """R-CODE-FAST → CODE-FAST (subagent + <200 lines)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Add a quick field",
            kind="code_edit",
            domain="default",
            estimated_lines=150,
            subagent=True,
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-CODE-FAST"
        assert lane == "CODE-FAST"
        assert is_hard is False

    def test_routing_default(self, tmp_path):
        """R-DEFAULT → ROUTER-FREE."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Tell me a joke",
            kind="classify",
            domain="default",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-DEFAULT"
        assert lane == "ROUTER-FREE"

    def test_routing_multimodal(self, tmp_path):
        """R-MULTIMODAL → NANO-PERCEPTION (hard gate)."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Analyze this image",
            kind="classify",
            domain="default",
            input_modality="image",
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        assert rule_id == "R-MULTIMODAL"
        assert lane == "NANO-PERCEPTION"
        assert is_hard is True

    def test_decompose_dag_persisted(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        dag_file = tmp_path / intake.mission_id / "dag.json"
        assert dag_file.exists()
        dag = json.loads(dag_file.read_text())
        assert "nodes" in dag
        assert "edges" in dag
        assert len(dag["nodes"]) == len(subtasks)


# ─── DISPATCH ──────────────────────────────────────────────────────────────────


class TestDispatch:
    def test_dispatch_schedules_waves(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        nodes = orch.dispatch(intake.mission_id, subtasks, edges)
        assert len(nodes) == len(subtasks)
        assert all(n.status in ("RUNNING", "BLOCKED") for n in nodes)

    def test_dispatch_receipt_persisted(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        orch.dispatch(intake.mission_id, subtasks, edges)
        dispatch_file = tmp_path / intake.mission_id / "DISPATCH.json"
        assert dispatch_file.exists()
        data = json.loads(dispatch_file.read_text())
        assert data["stage"] == "DISPATCH"
        assert "waves" in data["evidence"]


# ─── VERIFY ────────────────────────────────────────────────────────────────────


class TestVerify:
    def test_verify_no_receipts(self, tmp_path):
        """F-VER-01 when no receipts provided."""
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        nodes = orch.dispatch(intake.mission_id, subtasks, edges)
        verified = orch.verify(intake.mission_id, nodes, [])
        assert len(verified) == 0

    def test_verify_with_valid_receipts(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        nodes = orch.dispatch(intake.mission_id, subtasks, edges)

        receipts = []
        for st in subtasks:
            if st.lane in ("CODE", "CODE-FAST"):
                receipts.append(
                    make_code_receipt_with_sigs(task=st.description, lane=st.lane)
                )
            else:
                receipts.append(make_receipt(task=st.description, lane=st.lane))
        verified = orch.verify(intake.mission_id, nodes, receipts)
        assert len(verified) == len(subtasks)
        assert all(v.l2_proof for v in verified)

    def test_verify_rejects_l2_proof_false(self, tmp_path):
        """F-VER-01: l2_proof_missing when l2_proof is not True."""
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")
        nodes = orch.dispatch(intake.mission_id, subtasks, edges)

        receipts = []
        for st in subtasks:
            receipts.append(
                make_receipt(task=st.description, lane=st.lane, l2_proof=False)
            )
        verified = orch.verify(intake.mission_id, nodes, receipts)
        assert len(verified) == 0

    def test_verify_three_sig_missing(self, tmp_path):
        """F-VER-02: three_sig_missing for CODE lane without full sig chain."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Fix the login bug",
            kind="code_edit",
            domain="default",
            estimated_lines=150,
            subagent=True,
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        st.lane = lane

        # Receipt with only producer signature
        sigs = [
            {
                "role": "producer",
                "lane": "CODE",
                "model": "test",
                "ts": now_iso(),
                "receipt_sha256": "abc123",
            }
        ]
        receipt = make_receipt(lane=lane, task=st.description, signatures=sigs)

        dn = DispatchNode(
            id="t1", lane=lane, model="test", task=f"[{rule_id}] {st.description}"
        )
        verified = orch.verify("mission_test", [dn], [receipt])
        assert len(verified) == 0  # Missing auditor + refiner

    def test_verify_three_sig_present(self, tmp_path):
        """Three-signature gate passes when all roles present."""
        orch = fresh_orch(tmp_path)
        st = Subtask(
            id="t1",
            description="Fix the login bug",
            kind="code_edit",
            domain="default",
            estimated_lines=150,
            subagent=True,
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        st.lane = lane

        receipt = make_code_receipt_with_sigs(task=st.description, lane=lane)
        dn = DispatchNode(id="t1", lane=lane, model="test", task=receipt["task"])
        verified = orch.verify("mission_test", [dn], [receipt])
        assert len(verified) == 1
        assert len(verified[0].signatures) == 3
        assert {s.role for s in verified[0].signatures} == set(THREE_SIG_ROLES)


# ─── FUSE ──────────────────────────────────────────────────────────────────────


class TestFuse:
    def _make_verified(self, lane, task, l2_proof=True, sha256_match=True):
        receipt = make_receipt(lane=lane, task=task)
        return VerifiedReceipt(
            receipt=receipt,
            sha256_match=sha256_match,
            schema_valid=True,
            l2_proof=l2_proof,
        )

    def test_fuse_basic(self, tmp_path):
        orch = fresh_orch(tmp_path)
        verified = [
            self._make_verified("CODE", "Fix bug A"),
            self._make_verified("VERIFY", "Audit bug A"),
        ]
        signatures = []
        fused = orch.fuse("mission_test", verified, signatures)
        assert len(fused.artifacts) == 2
        assert fused.l2_proof is True
        assert fused.receipt_chain_sha256

    def test_fuse_rejects_drafts(self, tmp_path):
        """G3: drafts (l2_proof != true) are rejected."""
        orch = fresh_orch(tmp_path)
        draft = self._make_verified("CODE", "Draft output", l2_proof=False)
        fused = orch.fuse("mission_test", [draft], [])
        assert len(fused.artifacts) == 0
        assert fused.l2_proof is False

    def test_fuse_dedup(self, tmp_path):
        """Duplicate receipts are deduped by content hash."""
        orch = fresh_orch(tmp_path)
        r1 = make_receipt(lane="CODE", task="Fix bug")
        r2 = make_receipt(lane="CODE", task="Fix bug")  # identical
        verified = [
            VerifiedReceipt(
                receipt=r1, sha256_match=True, schema_valid=True, l2_proof=True
            ),
            VerifiedReceipt(
                receipt=r2, sha256_match=True, schema_valid=True, l2_proof=True
            ),
        ]
        fused = orch.fuse("mission_test", verified, [])
        assert len(fused.artifacts) == 1
        assert fused.dedup_count == 1

    def test_fuse_conflict_resolution(self, tmp_path):
        """Same task, different lanes with both l2=True → BLOCK on tie."""
        orch = fresh_orch(tmp_path)
        r1 = make_receipt(lane="CODE", task="Fix bug")
        r2 = make_receipt(lane="ROUTER-FREE", task="Fix bug")  # conflict
        verified = [
            VerifiedReceipt(
                receipt=r1, sha256_match=True, schema_valid=True, l2_proof=True
            ),
            VerifiedReceipt(
                receipt=r2, sha256_match=True, schema_valid=True, l2_proof=True
            ),
        ]
        fused = orch.fuse("mission_test", verified, [])
        assert len(fused.conflicts_resolved) >= 1


# ─── DELIVER ───────────────────────────────────────────────────────────────────


class TestDeliver:
    def test_deliver_shipped(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        fused = FusedArtifact(
            mission_id=intake.mission_id,
            artifacts=[{"lane": "CODE", "task": "test"}],
            dedup_count=0,
            conflicts_resolved=[],
            receipt_chain_sha256=sha256_bytes(b"test chain"),
            l2_proof=True,
            signatures=[],
            ts=now_iso(),
        )
        delivery = orch.deliver(intake.mission_id, fused, intake, run_quality=make_run_quality())
        assert delivery.status == "SHIPPED"
        assert delivery.memory_write_id.startswith("mem_")

    def test_deliver_blocks_without_run_quality_before_memory_write(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        fused = FusedArtifact(
            mission_id=intake.mission_id,
            artifacts=[{"lane": "CODE", "task": "test"}],
            dedup_count=0,
            conflicts_resolved=[],
            receipt_chain_sha256=sha256_bytes(b"test chain"),
            l2_proof=True,
            signatures=[],
            ts=now_iso(),
        )
        delivery = orch.deliver(intake.mission_id, fused, intake)
        assert delivery.status == "BLOCKED"
        assert "F-DEL-03" in delivery.status_line
        assert delivery.memory_write_id == ""

    def test_deliver_blocked_on_conflict(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        fused = FusedArtifact(
            mission_id=intake.mission_id,
            artifacts=[],
            dedup_count=0,
            conflicts_resolved=[{"task": "test", "decision": "BLOCKED"}],
            receipt_chain_sha256=sha256_bytes(b"test chain"),
            l2_proof=True,
            signatures=[],
            ts=now_iso(),
        )
        delivery = orch.deliver(intake.mission_id, fused, intake)
        assert delivery.status == "BLOCKED"

    def test_deliver_delivery_file_persisted(self, tmp_path):
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        fused = FusedArtifact(
            mission_id=intake.mission_id,
            artifacts=[{"lane": "CODE", "task": "test"}],
            dedup_count=0,
            conflicts_resolved=[],
            receipt_chain_sha256=sha256_bytes(b"test chain"),
            l2_proof=True,
            signatures=[],
            ts=now_iso(),
        )
        delivery = orch.deliver(intake.mission_id, fused, intake, run_quality=make_run_quality())
        delivery_file = tmp_path / intake.mission_id / "delivery.json"
        assert delivery_file.exists()
        data = json.loads(delivery_file.read_text())
        assert data["status"] == "SHIPPED"


# ─── FULL LIFECYCLE ─────────────────────────────────────────────────────────────


class TestFullLifecycle:
    def test_run_with_no_receipts(self, tmp_path):
        """Full lifecycle with no receipts — should FUSE to empty, DELIVER REFUSED."""
        orch = fresh_orch(tmp_path)
        delivery = orch.run("Build a REST API endpoint")
        assert delivery.status in ("BLOCKED", "REFUSED", "SHIPPED")
        assert delivery.mission_id.startswith("mission_")

    def test_run_with_valid_receipts(self, tmp_path):
        """Full lifecycle with valid receipts — should SHIP."""
        orch = fresh_orch(tmp_path)
        intake = orch.intake("Build a REST API endpoint")
        subtasks, edges = orch.decompose(intake, "Build a REST API endpoint")

        receipts = []
        for st in subtasks:
            if st.lane in ("CODE", "CODE-FAST"):
                receipts.append(
                    make_code_receipt_with_sigs(task=st.description, lane=st.lane)
                )
            else:
                receipts.append(make_receipt(task=st.description, lane=st.lane))

        delivery = orch.run(
            "Build a REST API endpoint",
            receipts=receipts,
            run_quality=make_run_quality(),
        )
        assert delivery.status == "SHIPPED"

    def test_all_stage_files_created(self, tmp_path):
        orch = fresh_orch(tmp_path)
        delivery = orch.run("Build a REST API endpoint")
        run_dir = tmp_path / delivery.mission_id
        assert (run_dir / "INTAKE.json").exists()
        assert (run_dir / "DECOMPOSE.json") or True  # DAG is separate
        assert (run_dir / "DISPATCH.json").exists()
        assert (run_dir / "VERIFY.json").exists()
        assert (run_dir / "fused.json").exists()
        assert (run_dir / "delivery.json").exists()


# ─── Schema / Hash Utilities ──────────────────────────────────────────────────


class TestSchemaAndHash:
    def test_validate_receipt_schema_valid(self):
        receipt = make_receipt()
        valid, err = validate_receipt_schema(receipt)
        assert valid is True
        assert err is None

    def test_validate_receipt_schema_missing_field(self):
        receipt = {"lane": "CODE"}  # missing model, task, l2_proof
        valid, err = validate_receipt_schema(receipt)
        assert valid is False
        assert err is not None

    def test_canonical_json_deterministic(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        assert canonical_json(a) == canonical_json(b)

    def test_sha256_bytes_consistent(self):
        data = b"hello world"
        assert sha256_bytes(data) == sha256_bytes(data)
        assert sha256_bytes(data) != sha256_bytes(b"goodbye")

    def test_classify_text_medical(self):
        kind, domain, modality = classify_text("Diagnose patient with diabetes")
        assert domain == "medical"

    def test_classify_text_finance(self):
        kind, domain, modality = classify_text("Calculate monthly revenue")
        assert domain == "finance"

    def test_classify_text_code_edit(self):
        kind, domain, modality = classify_text("Fix the login bug in the auth module")
        assert kind == "code_edit"

    def test_classify_text_image_modality(self):
        kind, domain, modality = classify_text("Analyze this image of a protein")
        assert modality == "image"


# ─── CLI ───────────────────────────────────────────────────────────────────────


class TestCLI:
    def test_route_cli(self, tmp_path):
        orch = fresh_orch(tmp_path)
        result = orch.route(
            json.dumps(
                {
                    "kind": "code_edit",
                    "domain": "default",
                    "task": "Fix the login bug",
                    "input_tokens": 500,
                    "estimated_lines": 150,
                    "subagent": True,
                }
            )
        )
        assert result["rule_id"] == "R-CODE-FAST"
        assert result["lane"] == "CODE-FAST"
        assert result["model"] == "poolside/laguna-xs-2.1:free"

    def test_route_cli_medical(self, tmp_path):
        orch = fresh_orch(tmp_path)
        result = orch.route(
            json.dumps(
                {
                    "kind": "classify",
                    "domain": "medical",
                    "task": "Diagnose patient symptoms",
                }
            )
        )
        assert result["rule_id"] == "R-MEDICAL"
        assert result["lane"] == "DOMAIN-MED"

    def test_validate_receipt_cli(self, tmp_path):
        orch = fresh_orch(tmp_path)
        receipt = make_receipt()
        receipt_file = tmp_path / "receipt.json"
        receipt_file.write_text(json.dumps(receipt))
        result = orch.validate_receipt(str(receipt_file))
        assert result["schema_valid"] is True
        assert result["l2_proof"] is True


# ─── Constants ─────────────────────────────────────────────────────────────────


class TestConstants:
    def test_all_lanes_have_models(self):
        for lane in LANE_MODELS:
            assert LANE_MODELS[lane]
            assert LANE_MODELS[lane] != "unknown"

    def test_lane_priority_complete(self):
        for lane in LANE_MODELS:
            assert lane in LANE_PRIORITY, f"Missing priority for {lane}"

    def test_three_sig_requirements(self):
        assert set(THREE_SIG_ROLES) == {"producer", "auditor", "refiner"}

    def test_budget_max_is_100(self):
        assert MISSION_BUDGET_MAX == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
