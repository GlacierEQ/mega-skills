#!/usr/bin/env python3
"""
apex-orchestration / scripts / orchestrator.py
Mission lifecycle engine implementing Packets 01-07 (v1.0.0) with
v1.1.0 (ML routing) and v1.2.0 (DAG scheduler) integration.

INTAKE -> DECOMPOSE -> DISPATCH -> VERIFY -> FUSE -> DELIVER

This is the operational layer that makes AGENTS.md actionable.
It does NOT call model APIs directly — it coordinates lane dispatch,
validates receipts, enforces gates, and produces the delivery contract.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ─── Imports from sibling modules ─────────────────────────────────────────────

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ml_routing import (  # noqa: E402
    select_lane,
    LaneStats,
    DEFAULT_STATE_ROOT,
    EMBEDDING_DIM,
    embed_intent,
    cosine,
)
from advanced import (  # noqa: E402
    DAGNode,
    detect_cycles,
    schedule_dag,
    propagate_block,
    check_constitution,
    DEFAULT_CONSTITUTION,
    MAX_PARALLEL,
    CACHE_THRESHOLD,
    RAG_THRESHOLD,
)

# ─── Constants ────────────────────────────────────────────────────────────────

MISSION_BUDGET_DEFAULT = 1.0
MISSION_BUDGET_MAX = 100.0
SCOPE_AMBIGUITY_THRESHOLD = 0.6
L2_PROOF_REQUIRED = True
THREE_SIG_ROLES = ("producer", "auditor", "refiner")

# Lane → model mapping (mirrors skill.py LANES, authoritative)
LANE_MODELS: Dict[str, str] = {
    "REASON": "nvidia/nemotron-3-ultra-550b-a550b:free",
    "CODE": "poolside/laguna-s-2.1:free",
    "CODE-FAST": "poolside/laguna-xs-2.1:free",
    "VERIFY": "z-ai/glm-5.2:free",
    "REVIEW": "cohere/north-mini-code:free",
    "LONG-CTX": "thinkingmachines/inkling:free",
    "LONG-CTX-ALT": "minimax/minimax-m3:free",
    "THINK-DEEP": "minimax/minimax-m2.7:free",
    "NANO-PERCEPTION": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "DOMAIN-MED": "inclusionai/ling-3.0-flash-sante:free",
    "DOMAIN-FIN": "inclusionai/ling-3.0-flash-fin:free",
    "ROUTER-FREE": "openrouter/free",
}

# Lane priority for FUSE sort (lower = first)
LANE_PRIORITY: Dict[str, int] = {
    "VERIFY": 0,
    "REVIEW": 1,
    "CODE": 2,
    "CODE-FAST": 2,
    "REASON": 3,
    "THINK-DEEP": 3,
    "DOMAIN-MED": 4,
    "DOMAIN-FIN": 4,
    "NANO-PERCEPTION": 4,
    "LONG-CTX": 5,
    "LONG-CTX-ALT": 5,
    "ROUTER-FREE": 6,
}

# Keyword-based subtask classifier (used when explicit subtasks aren't provided)
DOMAIN_KEYWORDS = {
    "medical": {
        "medical",
        "clinical",
        "patient",
        "diagnos",
        "treatment",
        "disease",
        "symptom",
    },
    "finance": {
        "finance",
        "revenue",
        "cost",
        "budget",
        "pricing",
        "roi",
        "cpa",
        "cac",
        "ltv",
    },
}

KIND_KEYWORDS = {
    "plan": {
        "plan",
        "design",
        "architect",
        "structure",
        "blueprint",
        "roadmap",
        "schedule",
    },
    "code_edit": {"fix", "edit", "refactor", "modify", "update", "change", "debug"},
    "code_create": {"create", "build", "implement", "write", "generate", "new"},
    "audit": {"audit", "review", "verify", "check", "test", "inspect"},
    "summarize": {"summarize", "summary", "shorten", "condense", "brief"},
    "classify": {"classify", "categorize", "label", "tag", "identify"},
}

MODALITY_KEYWORDS = {
    "image": {"image", "photo", "picture", "png", "jpg", "visual"},
    "video": {"video", "animation", "motion", "mp4", "gif"},
    "audio": {"audio", "sound", "voice", "speech", "wav", "mp3"},
}


# ─── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class Intake:
    """INTAKE stage receipt (Packet 02, stage A)."""

    mission_id: str
    scope: str
    budget: float
    blast_radius: str
    classification: str
    ts: str
    confidence: float = 1.0
    causes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": "INTAKE",
            "mission_id": self.mission_id,
            "ts": self.ts,
            "evidence": {
                "scope": self.scope,
                "budget": self.budget,
                "blast_radius": self.blast_radius,
                "classification": self.classification,
                "confidence": self.confidence,
            },
            "owner": "operator",
            "causes": self.causes,
        }


@dataclass
class Subtask:
    """A single unit of work in the DAG."""

    id: str
    description: str
    kind: str = "classify"
    domain: str = "default"
    input_modality: str = "text"
    input_tokens: int = 500
    invariants: int = 1
    cross_domain: bool = False
    estimated_lines: int = 0
    subagent: bool = False
    depends_on: List[str] = field(default_factory=list)
    # Filled by routing
    lane: str = ""
    rule_id: str = ""
    model: str = ""
    is_hard: bool = False
    score: float = 0.0


@dataclass
class DispatchNode:
    """Tracks a node through dispatch + verification."""

    id: str
    lane: str
    model: str
    task: str
    status: str = "PENDING"  # PENDING | READY | RUNNING | PASSED | FAILED | BLOCKED
    receipt: Optional[Dict[str, Any]] = None
    cause: Optional[str] = None
    signatures: List[str] = field(default_factory=list)


@dataclass
class Signature:
    """Three-signature rule (Packet 05, F-VER-02)."""

    role: str  # producer | auditor | refiner
    lane: str
    model: str
    ts: str
    receipt_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "lane": self.lane,
            "model": self.model,
            "ts": self.ts,
            "receipt_sha256": self.receipt_sha256,
        }


@dataclass
class VerifiedReceipt:
    """A receipt that has passed VERIFY stage."""

    receipt: Dict[str, Any]
    sha256_match: bool
    schema_valid: bool
    l2_proof: bool
    signatures: List[Signature] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FusedArtifact:
    """Output of FUSE stage (Packet 06)."""

    mission_id: str
    artifacts: List[Dict[str, Any]]
    dedup_count: int
    conflicts_resolved: List[Dict[str, Any]]
    receipt_chain_sha256: str
    l2_proof: bool
    signatures: List[Signature]
    ts: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": "FUSE",
            "mission_id": self.mission_id,
            "ts": self.ts,
            "evidence": {
                "artifacts": self.artifacts,
                "dedup_count": self.dedup_count,
                "conflicts_resolved": self.conflicts_resolved,
                "receipt_chain_sha256": self.receipt_chain_sha256,
                "l2_proof": self.l2_proof,
                "signatures": [s.to_dict() for s in self.signatures],
            },
            "owner": "operator",
        }


@dataclass
class Delivery:
    """Final delivery contract (Packet 07)."""

    mission_id: str
    status: str  # SHIPPED | BLOCKED | REFUSED
    compound_artifact: Dict[str, Any]
    status_line: str
    receipt_chain_sha256: str
    signatures: Dict[str, Any]
    memory_write_id: str
    causes: List[str]
    ts: str
    run_quality: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.run_quality is None:
            data.pop("run_quality", None)
        return data


# ─── Helper Functions ──────────────────────────────────────────────────────────


def ulid() -> str:
    """Generate a ULID-like identifier."""
    t = int(time.time() * 1000)
    r = uuid.uuid4().int & 0xFFFFFFFFFFFF
    return f"mission_{t:x}{r:012x}"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def canonical_json(obj: Any) -> bytes:
    """Canonical JSON serialization for chain hashing (Packet 03 G4)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_schema(name: str) -> Dict[str, Any]:
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / name
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_receipt_schema(receipt: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a receipt dict against the JSON schema (Packet 03 G1/G2/G3)."""
    schema = load_schema("receipt.schema.json")
    try:
        import jsonschema

        jsonschema.validate(receipt, schema)
        return (True, None)
    except ImportError:
        # Fallback: check required fields manually
        required = schema.get("required", [])
        missing = [k for k in required if k not in receipt]
        if missing:
            return (False, f"missing required fields: {missing}")
        if receipt.get("l2_proof") is not True:
            return (False, "l2_proof must be true")
        return (True, None)
    except jsonschema.ValidationError as e:
        return (False, str(e))


def validate_run_quality_evidence(run_quality: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """Validate the same fail-closed run-quality object required by delivery.schema.json."""
    if not run_quality:
        return (False, "run_quality evidence is required for SHIPPED")
    schema = load_schema("delivery.schema.json")["properties"]["run_quality"]
    try:
        import jsonschema
        jsonschema.validate(run_quality, schema)
        return (True, None)
    except ImportError:
        required = set(schema.get("required", []))
        missing = sorted(required - set(run_quality))
        if missing:
            return (False, f"missing run_quality fields: {missing}")
        source = run_quality.get("source_coverage", {})
        delta = run_quality.get("mission_delta", {})
        verification = run_quality.get("verification", {})
        if source.get("scope") not in {"bounded", "partial", "exhaustive"} or not source.get("evidence"):
            return (False, "source_coverage requires a valid scope and evidence")
        if delta.get("changed") is not True or not delta.get("before") or not delta.get("after"):
            return (False, "mission_delta must record changed=true with before/after")
        if not run_quality.get("durable_outputs"):
            return (False, "durable_outputs must contain at least one output")
        if verification.get("status") != "verified" or not verification.get("evidence"):
            return (False, "verification must be verified with evidence")
        if not run_quality.get("next_frontier"):
            return (False, "next_frontier is required")
        return (True, None)
    except jsonschema.ValidationError as exc:
        return (False, exc.message)


# ─── Subtask Classification ────────────────────────────────────────────────────


def classify_text(text: str) -> Tuple[str, str, str]:
    """
    Heuristic classifier for subtask kind, domain, modality.
    Returns (kind, domain, input_modality).

    This is a keyword-based fallback. In production, this would be
    replaced by an actual model call through the REASON lane.
    """
    text_lower = text.lower()

    # Domain
    domain = "default"
    for d, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            domain = d
            break

    # Modality
    modality = "text"
    for m, keywords in MODALITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            modality = m
            break

    # Kind
    kind = "classify"
    scores: List[Tuple[str, int]] = []
    for k, keywords in KIND_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            scores.append((k, count))
    if scores:
        scores.sort(key=lambda x: -x[1])
        kind = scores[0][0]

    return kind, domain, modality


def decompose_description(
    description: str, budget: float = MISSION_BUDGET_DEFAULT
) -> Tuple[List[Subtask], str, str, float]:
    """
    Heuristic decomposition of a natural-language mission description
    into an ordered list of subtasks.

    Returns (subtasks, scope, classification, confidence).

    In production, the REASON lane would perform decomposition.
    Here we use keyword-based heuristics as a fallback.
    """
    text_lower = description.lower()

    # Determine classification
    classification = "local"
    if "remote" in text_lower or "deploy" in text_lower or "production" in text_lower:
        classification = "remote"
    if "destructive" in text_lower or "delete" in text_lower or "drop" in text_lower:
        classification = "destructive"
    if "cross-domain" in text_lower or "multi-domain" in text_lower:
        classification = "cross_domain"

    # Estimate scope and confidence
    word_count = len(description.split())
    scope = "bounded" if word_count < 50 else "exploratory"
    confidence = min(1.0, max(0.3, word_count / 100.0))

    # Determine if this is a plan-type or code-type task
    kind, domain, modality = classify_text(description)

    # Build subtask chain
    subtasks: List[Subtask] = []

    # Task 1: Classification (always first)
    subtasks.append(
        Subtask(
            id="task-0",
            description="Classify task type and domain",
            kind="classify",
            domain=domain,
            input_modality=modality,
            estimated_lines=0,
        )
    )

    # Task 2: Main task
    subtasks.append(
        Subtask(
            id="task-1",
            description=description,
            kind=kind,
            domain=domain,
            input_modality=modality,
            input_tokens=min(word_count * 2, 4096),
            estimated_lines=word_count if kind in ("code_edit", "code_create") else 0,
        )
    )

    # Task 3: Verification (depends on task-1)
    subtasks[-1].depends_on = ["task-0"]
    subtasks.append(
        Subtask(
            id="task-2",
            description="Verify output against requirements",
            kind="audit",
            domain=domain,
            input_modality=modality,
            depends_on=["task-1"],
        )
    )

    # For code tasks, add review
    if kind in ("code_edit", "code_create"):
        subtasks.append(
            Subtask(
                id="task-3",
                description="Review code for quality and complexity",
                kind="audit",
                domain=domain,
                input_modality=modality,
                depends_on=["task-1"],
            )
        )

    return subtasks, scope, classification, confidence


def route_subtask(
    subtask: Subtask, learned_state: Dict[str, LaneStats]
) -> Tuple[str, str, bool, float]:
    """
    Route a single subtask through the 8-rule heuristics (Packet 04),
    then score with the learned routing function (Packet 13).

    Returns (rule_id, lane, is_hard, score).
    """
    subtask_dict = {
        "id": subtask.id,
        "kind": subtask.kind,
        "domain": subtask.domain,
        "input_modality": subtask.input_modality,
        "input_tokens": subtask.input_tokens,
        "invariants": subtask.invariants,
        "cross_domain": subtask.cross_domain,
        "estimated_lines": subtask.estimated_lines,
        "subagent": subtask.subagent,
        "task": subtask.description,
    }

    rule_id, lane, score = select_lane(subtask_dict, learned_state)

    # Determine if the matched rule is hard-gated
    is_hard = False
    rule_hardness = {
        "R-MEDICAL": True,
        "R-FINANCE": True,
        "R-MULTIMODAL": True,
        "R-LONGCTX": True,
        "R-PLAN": True,
        "R-CODE-EDIT": False,
        "R-CODE-FAST": False,
        "R-DEFAULT": False,
    }
    is_hard = rule_hardness.get(rule_id, False)

    model = LANE_MODELS.get(lane, "unknown")
    return rule_id, lane, is_hard, score


# ─── Mission Orchestrator ─────────────────────────────────────────────────────


class MissionOrchestrator:
    """
    Runs the 6-stage mission lifecycle.

    INTAKE -> DECOMPOSE -> DISPATCH -> VERIFY -> FUSE -> DELIVER

    Usage:
        orch = MissionOrchestrator()
        delivery = orch.run("Build a REST API endpoint")

    The orchestrator does not call model APIs. It coordinates lane dispatch,
    validates receipts, enforces gates, and produces the delivery contract.
    Actual model invocation is performed by the operator / lane workers.
    """

    def __init__(
        self,
        state_root: Optional[Path] = None,
        learned_state: Optional[Dict[str, LaneStats]] = None,
    ) -> None:
        self.state_root = state_root or (DEFAULT_STATE_ROOT / "missions")
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.lane_stats: Dict[str, LaneStats] = learned_state or {}

    # ─── Stage 1: INTAKE ─────────────────────────────────────────────────

    def intake(
        self,
        description: str,
        budget: float = MISSION_BUDGET_DEFAULT,
        blast_radius: str = "local",
        scope: str = "",
    ) -> Intake:
        """INTAKE stage: validate scope, declare budget and blast radius.

        F-INT-01: scope_ambiguous if confidence < 0.6
        F-INT-02: budget_exceeded if budget > MISSION_BUDGET_MAX
        """
        mission_id = ulid()
        ts = now_iso()

        # Classify and decompose to estimate confidence
        subtasks, inferred_scope, classification, confidence = decompose_description(
            description, budget
        )

        if not scope:
            scope = inferred_scope

        causes: List[str] = []

        if confidence < SCOPE_AMBIGUITY_THRESHOLD:
            causes.append(f"F-INT-01 scope_ambiguous: confidence={confidence:.2f}")

        if budget > MISSION_BUDGET_MAX:
            causes.append(
                f"F-INT-02 budget_exceeded: budget={budget} > max={MISSION_BUDGET_MAX}"
            )

        intake = Intake(
            mission_id=mission_id,
            scope=scope,
            budget=budget,
            blast_radius=blast_radius,
            classification=classification,
            ts=ts,
            confidence=confidence,
            causes=causes,
        )

        # Persist INTAKE receipt
        self._write_stage_receipt(mission_id, "INTAKE", intake.to_dict())

        return intake

    # ─── Stage 2: DECOMPOSE ────────────────────────────────────────────────

    def decompose(
        self, intake: Intake, description: str
    ) -> Tuple[List[Subtask], List[Tuple[str, str]]]:
        """DECOMPOSE stage: split mission into subtasks, route each to a lane,
        build dependency DAG.

        F-DEC-01: dag_cycle if the DAG has a cycle
        F-DEC-02: lane_unavailable if selected lane is unhealthy
        """
        subtasks, _, _, _ = decompose_description(description, intake.budget)

        # Route each subtask
        routed: List[Subtask] = []
        for st in subtasks:
            rule_id, lane, is_hard, score = route_subtask(st, self.lane_stats)
            st.lane = lane
            st.rule_id = rule_id
            st.model = LANE_MODELS.get(lane, "unknown")
            st.is_hard = is_hard
            st.score = score
            routed.append(st)

        # Check for cycles (Packet 19 G1)
        nodes_dict = {
            st.id: DAGNode(id=st.id, lane=st.lane, gate="L2", depends_on=st.depends_on)
            for st in routed
        }

        if detect_cycles(nodes_dict):
            raise ValueError("F-DEC-01 dag_cycle detected in decomposed DAG")

        # Build DAG edges
        edges: List[Tuple[str, str]] = []
        for st in routed:
            for dep in st.depends_on:
                edges.append((dep, st.id))

        dag = {
            "mission_id": intake.mission_id,
            "nodes": [asdict(st) for st in routed],
            "edges": [{"from": e[0], "to": e[1]} for e in edges],
        }
        self._write_dag(intake.mission_id, dag)

        return routed, edges

    # ─── Stage 3: DISPATCH ─────────────────────────────────────────────────

    def dispatch(
        self,
        mission_id: str,
        subtasks: List[Subtask],
        edges: List[Tuple[str, str]],
        max_parallel: int = MAX_PARALLEL,
    ) -> List[DispatchNode]:
        """DISPATCH stage: schedule DAG waves, dispatch each node.

        Uses Packet 19 DAG scheduler (Kahn's algorithm, wave-based).
        F-DIS-01: dispatch_timeout if no receipt within timeout
        F-DIS-02: quota_exhausted if lane reports quota exhausted
        """
        # Build DAG nodes from subtasks
        nodes: Dict[str, DAGNode] = {}
        for st in subtasks:
            nodes[st.id] = DAGNode(
                id=st.id, lane=st.lane, gate="L2", depends_on=st.depends_on
            )

        # Compute execution waves
        try:
            waves = schedule_dag(nodes, max_parallel=max_parallel)
        except ValueError as e:
            if "F-DEC-01" in str(e):
                raise
            raise ValueError(f"F-DIS-01 dispatch_timeout: {e}")

        dispatch_nodes: List[DispatchNode] = []
        node_map = {st.id: st for st in subtasks}

        # Dispatch each wave
        for wave in waves:
            for node_id in wave:
                st = node_map.get(node_id)
                if not st:
                    continue
                dn = DispatchNode(
                    id=node_id,
                    lane=st.lane,
                    model=st.model,
                    task=st.description,
                )

                # Check quota (G5 from Packet 04)
                stats = self.lane_stats.get(st.lane)
                if stats and stats.quota_burn >= 1.0:
                    dn.status = "BLOCKED"
                    dn.cause = "F-DIS-02 quota_exhausted"
                else:
                    dn.status = "RUNNING"
                    dn.task = f"[{st.rule_id}] {st.description}"

                dispatch_nodes.append(dn)

        # Record dispatch decision
        dispatch_receipt = {
            "stage": "DISPATCH",
            "mission_id": mission_id,
            "ts": now_iso(),
            "evidence": {
                "waves": waves,
                "nodes": [asdict(n) for n in dispatch_nodes],
                "max_parallel": max_parallel,
            },
            "owner": "orchestrator",
        }
        self._write_stage_receipt(mission_id, "DISPATCH", dispatch_receipt)

        return dispatch_nodes

    # ─── Stage 4: VERIFY ───────────────────────────────────────────────────

    def verify(
        self,
        mission_id: str,
        dispatch_nodes: List[DispatchNode],
        receipts: List[Dict[str, Any]],
    ) -> List[VerifiedReceipt]:
        """VERIFY stage: validate receipts against schema, check SHA-256,
        enforce three-signature rule for code subtasks.

        F-VER-01: l2_proof_missing — receipt lacks l2_proof or sha256 mismatch
        F-VER-02: three_sig_missing — code subtask missing auditor or refiner
        """
        # Index receipts by parent_mission_id + task
        receipt_by_task = {}
        for r in receipts:
            key = r.get("task", "")
            receipt_by_task[key] = r

        # Index receipts by node id (match task to node)
        verified: List[VerifiedReceipt] = []
        re_dispatches: List[Dict[str, Any]] = []

        for dn in dispatch_nodes:
            if dn.status in ("BLOCKED",):
                continue

            # Find matching receipt
            receipt = None
            for r in receipts:
                task = r.get("task", "")
                if dn.task in task or task in dn.task:
                    receipt = r
                    break

            if receipt is None:
                re_dispatches.append(
                    {
                        "node_id": dn.id,
                        "cause": "F-VER-01 l2_proof_missing: no receipt found",
                        "action": "re_dispatch",
                    }
                )
                continue

            # Validate schema
            valid, err = validate_receipt_schema(receipt)
            if not valid:
                re_dispatches.append(
                    {
                        "node_id": dn.id,
                        "cause": f"F-VER-01 schema_invalid: {err}",
                        "action": "re_dispatch",
                    }
                )
                continue

            # Check l2_proof
            if not receipt.get("l2_proof") is True:
                re_dispatches.append(
                    {
                        "node_id": dn.id,
                        "cause": "F-VER-01 l2_proof_missing: not true",
                        "action": "re_dispatch",
                    }
                )
                continue

            # Verify SHA-256 against files_changed (G1 from Packet 03)
            sha256_match = True
            files_changed = receipt.get("files_changed", [])
            receipt_sha256 = receipt.get("sha256", [])
            if len(receipt_sha256) < len(files_changed):
                sha256_match = False
            else:
                for i, fpath in enumerate(files_changed):
                    if i >= len(receipt_sha256):
                        sha256_match = False
                        break
                    p = Path(fpath)
                    if p.exists():
                        actual = sha256_file(p)
                        expected = receipt_sha256[i]
                        if actual != expected:
                            sha256_match = False
                            break

            # Three-signature rule for code subtasks (Packet 05 G3)
            signatures: List[Signature] = []
            is_code = dn.lane in ("CODE", "CODE-FAST")
            if is_code:
                # Check if we have producer, auditor, refiner signatures
                sig_data = receipt.get("signatures", [])
                for s in sig_data:
                    signatures.append(
                        Signature(
                            role=s.get("role", ""),
                            lane=s.get("lane", ""),
                            model=s.get("model", ""),
                            ts=s.get("ts", ""),
                            receipt_sha256=s.get("receipt_sha256", ""),
                        )
                    )

                roles_present = {s.role for s in signatures}
                missing = set(THREE_SIG_ROLES) - roles_present
                if missing:
                    re_dispatches.append(
                        {
                            "node_id": dn.id,
                            "cause": f"F-VER-02 three_sig_missing: {', '.join(missing)}",
                            "action": "re_dispatch_missing_signature",
                        }
                    )
                    continue

            vr = VerifiedReceipt(
                receipt=receipt,
                sha256_match=sha256_match,
                schema_valid=valid,
                l2_proof=True,
                signatures=signatures,
            )
            verified.append(vr)

        verify_receipt = {
            "stage": "VERIFY",
            "mission_id": mission_id,
            "ts": now_iso(),
            "evidence": {
                "verified": len(verified),
                "re_dispatches": re_dispatches,
                "proofs": [
                    {
                        "node_id": vr.receipt.get("task", ""),
                        "sha256_match": vr.sha256_match,
                        "schema_valid": vr.schema_valid,
                        "l2_proof": vr.l2_proof,
                    }
                    for vr in verified
                ],
            },
            "owner": "VERIFY",
        }
        self._write_stage_receipt(mission_id, "VERIFY", verify_receipt)

        return verified

    # ─── Stage 5: FUSE ─────────────────────────────────────────────────────

    def fuse(
        self,
        mission_id: str,
        verified: List[VerifiedReceipt],
        signatures: List[Signature],
    ) -> FusedArtifact:
        """FUSE stage: merge verified receipts, dedup, resolve conflicts.

        G3 from Packet 06: drafts (l2_proof != true) are rejected.
        """
        # Step 1: filter verified receipts with l2_proof == true
        valid = [vr for vr in verified if vr.l2_proof and vr.schema_valid]

        # Step 2: sort by lane_priority, then ts
        def sort_key(vr: VerifiedReceipt) -> Tuple[int, str]:
            lane = vr.receipt.get("lane", "ROUTER-FREE")
            return (LANE_PRIORITY.get(lane, 99), vr.receipt.get("task", ""))

        valid.sort(key=sort_key)

        # Step 3: deduplicate by content hash
        seen_hashes: Set[str] = set()
        artifacts: List[Dict[str, Any]] = []
        dedup_count = 0
        conflicts: List[Dict[str, Any]] = []

        for vr in valid:
            receipt = vr.receipt
            # Normalize: strip whitespace, collapse comments
            text = json.dumps(receipt, sort_keys=True)
            content_hash = sha256_bytes(text.encode("utf-8"))

            if content_hash in seen_hashes:
                dedup_count += 1
                continue
            seen_hashes.add(content_hash)

            # Check for conflicts with existing artifacts
            # Conflict = same task, different output
            conflict_found = False
            for existing in artifacts:
                if existing.get("task") == receipt.get("task") and existing.get(
                    "lane"
                ) != receipt.get("lane"):
                    # Conflict resolution: dominant-verified evidence (Packet 06)
                    both_l2 = existing.get("l2_proof") and receipt.get("l2_proof")
                    if both_l2:
                        # Pick the one with sha256 verified
                        if vr.sha256_match and not existing.get("_sha256_verified"):
                            artifacts.remove(existing)
                            artifacts.append({**receipt, "_sha256_verified": True})
                        else:
                            # Tie: BLOCK with both options
                            conflicts.append(
                                {
                                    "task": receipt.get("task", ""),
                                    "a": existing.get("lane", ""),
                                    "b": receipt.get("lane", ""),
                                    "decision": "BLOCKED — tie, no dominant evidence",
                                }
                            )
                            conflict_found = True
                    elif receipt.get("l2_proof"):
                        artifacts.remove(existing)
                        artifacts.append(
                            {**receipt, "_sha256_verified": vr.sha256_match}
                        )
                    else:
                        conflict_found = True

            if not conflict_found:
                artifacts.append({**receipt, "_sha256_verified": vr.sha256_match})

        # Step 5: compute chain hash (Packet 03)
        chain_input = b"".join(canonical_json(vr.receipt) for vr in valid)
        chain_hash = sha256_bytes(chain_input)

        fused = FusedArtifact(
            mission_id=mission_id,
            artifacts=artifacts,
            dedup_count=dedup_count,
            conflicts_resolved=conflicts,
            receipt_chain_sha256=chain_hash,
            l2_proof=all(vr.l2_proof for vr in verified),
            signatures=signatures,
            ts=now_iso(),
        )

        self._write_fused(mission_id, fused.to_dict())

        return fused

    # ─── Stage 6: DELIVER ──────────────────────────────────────────────────

    def deliver(
        self,
        mission_id: str,
        fused: FusedArtifact,
        intake: Intake,
        run_quality: Optional[Dict[str, Any]] = None,
    ) -> Delivery:
        """DELIVER stage: produce final delivery contract.

        F-DEL-01: memory_write_failed
        F-DEL-02: chain_hash_drift
        """
        run_dir = self._run_dir(mission_id)
        receipts_dir = run_dir / "receipts"

        # Collect all staged receipts
        staged_receipts: List[Dict[str, Any]] = []
        if receipts_dir.exists():
            for f in sorted(receipts_dir.glob("*.json")):
                staged_receipts.append(json.loads(f.read_text()))

        # Recompute chain hash to verify reproducibility (F-DEL-02)
        if staged_receipts:
            chain_input = b"".join(canonical_json(r) for r in staged_receipts)
            chain_hash = sha256_bytes(chain_input)
        else:
            chain_hash = fused.receipt_chain_sha256

        if chain_hash != fused.receipt_chain_sha256:
            delivery = Delivery(
                mission_id=mission_id,
                status="REFUSED",
                compound_artifact={},
                status_line="F-DEL-02 chain_hash_drift: staged receipts do not match fused chain hash",
                receipt_chain_sha256=fused.receipt_chain_sha256,
                signatures={s.role: s.to_dict() for s in fused.signatures},
                memory_write_id="",
                causes=["F-DEL-02 chain_hash_drift"],
                ts=now_iso(),
            )
            self._write_delivery(mission_id, delivery.to_dict())
            return delivery

        # Check for conflicts that couldn't be resolved
        if fused.conflicts_resolved:
            delivery = Delivery(
                mission_id=mission_id,
                status="BLOCKED",
                compound_artifact={},
                status_line=f"F-FUSE-02: {len(fused.conflicts_resolved)} conflict(s) unresolved",
                receipt_chain_sha256=fused.receipt_chain_sha256,
                signatures={s.role: s.to_dict() for s in fused.signatures},
                memory_write_id="",
                causes=[c["decision"] for c in fused.conflicts_resolved],
                ts=now_iso(),
            )
            self._write_delivery(mission_id, delivery.to_dict())
            return delivery

        # SHIPPED is impossible without explicit source coverage, mission delta,
        # durable outputs, verification evidence, and the exact next frontier.
        run_quality_valid, run_quality_error = validate_run_quality_evidence(run_quality)
        if not run_quality_valid:
            delivery = Delivery(
                mission_id=mission_id,
                status="BLOCKED",
                compound_artifact={},
                status_line=f"F-DEL-03 run_quality_invalid: {run_quality_error}",
                receipt_chain_sha256=fused.receipt_chain_sha256,
                signatures={s.role: s.to_dict() for s in fused.signatures},
                memory_write_id="",
                causes=[f"F-DEL-03 run_quality_invalid: {run_quality_error}"],
                ts=now_iso(),
            )
            self._write_delivery(mission_id, delivery.to_dict())
            return delivery

        # Persist memory only after the run-quality proof passes.
        memory_write_id = self._write_memory(
            key=f"mission:{mission_id}",
            value={
                "summary": intake.scope,
                "artifact_path": str(run_dir / "fused.json"),
                "receipt_chain_sha256": fused.receipt_chain_sha256,
            },
            tags=["apex", "delivered", intake.classification],
        )

        if not memory_write_id:
            delivery = Delivery(
                mission_id=mission_id,
                status="BLOCKED",
                compound_artifact={},
                status_line="F-DEL-01 memory_write_failed",
                receipt_chain_sha256=fused.receipt_chain_sha256,
                signatures={s.role: s.to_dict() for s in fused.signatures},
                memory_write_id="",
                causes=["F-DEL-01 memory_write_failed"],
                ts=now_iso(),
            )
            self._write_delivery(mission_id, delivery.to_dict())
            return delivery

        delivery = Delivery(
            mission_id=mission_id,
            status="SHIPPED",
            compound_artifact={
                "artifacts": fused.artifacts,
                "dedup_count": fused.dedup_count,
                "conflicts_resolved": fused.conflicts_resolved,
            },
            status_line=f"Mission {mission_id} shipped: {len(fused.artifacts)} artifact(s), "
            f"{fused.dedup_count} dedup'd, chain={fused.receipt_chain_sha256[:16]}...",
            receipt_chain_sha256=fused.receipt_chain_sha256,
            signatures={s.role: s.to_dict() for s in fused.signatures},
            memory_write_id=memory_write_id,
            causes=[],
            ts=now_iso(),
            run_quality=run_quality,
        )

        self._write_delivery(mission_id, delivery.to_dict())

        return delivery

    # ─── Full Lifecycle ────────────────────────────────────────────────────

    def run(
        self,
        description: str,
        budget: float = MISSION_BUDGET_DEFAULT,
        blast_radius: str = "local",
        receipts: Optional[List[Dict[str, Any]]] = None,
        signatures: Optional[List[Signature]] = None,
        run_quality: Optional[Dict[str, Any]] = None,
    ) -> Delivery:
        """Run the full 6-stage lifecycle.

        Args:
            description: natural-language mission description
            budget: token/cost budget
            blast_radius: local | remote | cross_domain
            receipts: optional list of pre-existing verified receipts (for
                      testing / simulation without actual model calls)
            signatures: optional pre-existing three-signature set
            run_quality: source coverage, mission delta, durable outputs,
                         verification evidence, and exact next frontier
        """
        # Stage 1: INTAKE
        intake = self.intake(description, budget, blast_radius)

        # Stage 2: DECOMPOSE
        subtasks, edges = self.decompose(intake, description)

        # Stage 3: DISPATCH
        dispatch_nodes = self.dispatch(intake.mission_id, subtasks, edges)

        # Stage 4: VERIFY
        verified = self.verify(intake.mission_id, dispatch_nodes, receipts or [])

        # Collect signatures from verified receipts
        all_signatures: List[Signature] = signatures or []
        for vr in verified:
            for s in vr.signatures:
                all_signatures.append(s)

        # Stage 5: FUSE
        fused = self.fuse(intake.mission_id, verified, all_signatures)

        # Stage 6: DELIVER
        delivery = self.deliver(intake.mission_id, fused, intake, run_quality=run_quality)

        return delivery

    # ─── CLI: single-task routing ─────────────────────────────────────────

    def route(self, subtask_json: str) -> Dict[str, Any]:
        """CLI: route a single subtask and return lane + rule + score."""
        subtask_dict = json.loads(subtask_json)
        st = Subtask(
            id=subtask_dict.get("id", "unspecified"),
            description=subtask_dict.get("description", subtask_dict.get("task", "")),
            kind=subtask_dict.get("kind", "classify"),
            domain=subtask_dict.get("domain", "default"),
            input_modality=subtask_dict.get("input_modality", "text"),
            input_tokens=subtask_dict.get("input_tokens", 500),
            invariants=subtask_dict.get("invariants", 1),
            cross_domain=subtask_dict.get("cross_domain", False),
            estimated_lines=subtask_dict.get("estimated_lines", 0),
            subagent=subtask_dict.get("subagent", False),
        )
        rule_id, lane, is_hard, score = route_subtask(st, self.lane_stats)
        return {
            "rule_id": rule_id,
            "lane": lane,
            "model": LANE_MODELS.get(lane, "unknown"),
            "is_hard": is_hard,
            "score": score,
        }

    # ─── CLI: receipt validation ──────────────────────────────────────────

    def validate_receipt(self, receipt_path: str) -> Dict[str, Any]:
        """CLI: validate a receipt file against the schema + gates."""
        receipt = json.loads(Path(receipt_path).read_text())
        valid, err = validate_receipt_schema(receipt)

        result = {
            "file": receipt_path,
            "schema_valid": valid,
            "error": err,
            "l2_proof": receipt.get("l2_proof"),
            "has_sha256": len(receipt.get("sha256", [])) > 0,
            "files_changed": len(receipt.get("files_changed", [])),
        }

        # Check sha256 against actual files
        if valid and receipt.get("l2_proof") is True:
            files = receipt.get("files_changed", [])
            hashes = receipt.get("sha256", [])
            drift = []
            for i, f in enumerate(files):
                if i < len(hashes):
                    p = Path(f)
                    if p.exists():
                        actual = sha256_file(p)
                        if actual != hashes[i]:
                            drift.append(f)
            result["sha256_drift"] = drift

        # Check three-signature for code
        if valid and receipt.get("lane") in ("CODE", "CODE-FAST"):
            sigs = receipt.get("signatures", [])
            roles = {s.get("role") for s in sigs}
            missing = set(THREE_SIG_ROLES) - roles
            result["code_subtask"] = True
            result["signatures_present"] = sorted(roles)
            result["missing_signatures"] = sorted(missing) if missing else None

        return result

    # ─── Persistence ──────────────────────────────────────────────────────

    def _run_dir(self, mission_id: str) -> Path:
        return self.state_root / mission_id

    def _write_stage_receipt(
        self, mission_id: str, stage: str, data: Dict[str, Any]
    ) -> None:
        run_dir = self._run_dir(mission_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / f"{stage}.json").write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _write_dag(self, mission_id: str, dag: Dict[str, Any]) -> None:
        run_dir = self._run_dir(mission_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "dag.json").write_text(
            json.dumps(dag, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _write_fused(self, mission_id: str, data: Dict[str, Any]) -> None:
        run_dir = self._run_dir(mission_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "fused.json").write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _write_delivery(self, mission_id: str, data: Dict[str, Any]) -> None:
        run_dir = self._run_dir(mission_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "delivery.json").write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _write_memory(self, key: str, value: Dict[str, Any], tags: List[str]) -> str:
        """Append-only memory write (Packet 08)."""
        mem_root = DEFAULT_STATE_ROOT / "memory"
        mem_root.mkdir(parents=True, exist_ok=True)

        mem_id = f"mem_{uuid.uuid4().int & 0xFFFFFFFFFFFFFFFF:016x}"
        record = {
            "key": key,
            "value": value,
            "tags": tags,
            "ts": now_iso(),
            "schema_version": 1,
        }

        log_path = mem_root / "memory.log"
        with open(log_path, "a") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")

        # Write the value to a queryable file
        (mem_root / f"{mem_id}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return mem_id

    def _write_receipt(self, mission_id: str, receipt: Dict[str, Any]) -> None:
        """Append a receipt to the mission's receipt log."""
        run_dir = self._run_dir(mission_id)
        receipts_dir = run_dir / "receipts"
        receipts_dir.mkdir(parents=True, exist_ok=True)

        task = receipt.get("task", "unknown")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", task)[:60]
        receipt_path = (
            receipts_dir / f"{receipt.get('lane', 'unknown').lower()}_{safe_name}.json"
        )

        # Find an available name
        counter = 0
        while receipt_path.exists():
            receipt_path = (
                receipts_dir
                / f"{receipt.get('lane', 'unknown').lower()}_{safe_name}_{counter}.json"
            )
            counter += 1

        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True),
            encoding="utf-8",
        )


# ─── CLI Entry Point ───────────────────────────────────────────────────────────


def main(argv: List[str] | None = None) -> int:
    """CLI for routing a single subtask or running a full mission lifecycle."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="orchestrator.py",
        description="APEX Mesh Orchestrator — lane dispatch + mission lifecycle",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_route = sub.add_parser("route", help="Route a single subtask to a lane")
    p_route.add_argument(
        "--subtask-json",
        required=True,
        help="JSON object with subtask fields (kind, domain, task/description, "
        "input_tokens, input_modality, estimated_lines, subagent, etc.)",
    )

    p_mission = sub.add_parser("mission", help="Run full 6-stage mission lifecycle")
    p_mission.add_argument(
        "--description", required=True, help="Natural-language mission description"
    )
    p_mission.add_argument(
        "--budget", type=float, default=MISSION_BUDGET_DEFAULT, help="Token budget"
    )
    p_mission.add_argument(
        "--blast-radius",
        default="local",
        choices=["local", "remote", "cross_domain"],
        help="Mission blast radius",
    )
    p_mission.add_argument(
        "--receipts-json",
        default="[]",
        help="JSON array of pre-existing receipts (for testing/simulation)",
    )
    p_mission.add_argument(
        "--run-quality-json",
        default="",
        help="JSON run-quality proof required for SHIPPED",
    )

    p_validate = sub.add_parser("validate-receipt", help="Validate a receipt file")
    p_validate.add_argument("--path", required=True, help="Path to receipt JSON file")

    args = parser.parse_args(argv)

    orch = MissionOrchestrator()

    if args.command == "route":
        subtask_dict = json.loads(args.subtask_json)
        st = Subtask(
            id=subtask_dict.get("id", "unspecified"),
            description=subtask_dict.get("description", subtask_dict.get("task", "")),
            kind=subtask_dict.get("kind", "classify"),
            domain=subtask_dict.get("domain", "default"),
            input_modality=subtask_dict.get("input_modality", "text"),
            input_tokens=subtask_dict.get("input_tokens", 500),
            invariants=subtask_dict.get("invariants", 1),
            cross_domain=subtask_dict.get("cross_domain", False),
            estimated_lines=subtask_dict.get("estimated_lines", 0),
            subagent=subtask_dict.get("subagent", False),
        )
        rule_id, lane, is_hard, score = route_subtask(st, orch.lane_stats)
        result = {
            "rule_id": rule_id,
            "lane": lane,
            "model": LANE_MODELS.get(lane, "unknown"),
            "is_hard": is_hard,
            "score": score,
        }
        print(json.dumps(result, indent=2))
        return 0

    elif args.command == "mission":
        receipts = json.loads(args.receipts_json) if args.receipts_json else []
        run_quality = json.loads(args.run_quality_json) if args.run_quality_json else None
        delivery = orch.run(
            description=args.description,
            budget=args.budget,
            blast_radius=args.blast_radius,
            receipts=receipts,
            run_quality=run_quality,
        )
        print(json.dumps(delivery.to_dict(), indent=2))
        return 0 if delivery.status == "SHIPPED" else 1

    elif args.command == "validate-receipt":
        result = orch.validate_receipt(args.path)
        print(json.dumps(result, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
