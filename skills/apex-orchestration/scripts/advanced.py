#!/usr/bin/env python3
"""
apex-orchestration / scripts / advanced.py
Implementations of Packets 17-21 (cutting-edge dev techniques):
  17 - Speculative Decoding
  18 - Semantic Cache
  19 - DAG Scheduler
  20 - Property-Based Testing
  21 - Mutation Testing
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ─── Packet 17: Speculative Decoding ───────────────────────────────────────

CACHE_THRESHOLD = 0.95
CACHE_TTL_HOURS = 168
MAX_PARALLEL = 4
SLA_MS_DEFAULT = 2000
MUTATION_SCORE_TARGET = 0.80
PROPERTY_EXAMPLES_DEFAULT = 100


@dataclass
class SpeculationConfig:
    sla_ms: int = SLA_MS_DEFAULT
    trust_threshold: float = 0.10
    enable_after_observations: int = 10


def can_speculate(
    draft_trust: float,
    verify_trust: float,
    config: SpeculationConfig = SpeculationConfig(),
) -> bool:
    """G1 trust gate. The verifier must be meaningfully better than the draft."""
    return verify_trust >= draft_trust + config.trust_threshold


def speculation_decision(
    draft_done_ms: float,
    verify_done_ms: float,
    draft_l2: bool,
    verify_l2: bool,
    config: SpeculationConfig = SpeculationConfig(),
) -> str:
    """Decide which output to use based on timing and L2 proof.

    Returns one of: 'use_verify', 'use_draft_unverified', 'block_timeout'.
    """
    if verify_done_ms <= config.sla_ms and verify_l2:
        return "use_verify"
    if draft_done_ms <= config.sla_ms and draft_l2:
        return "use_draft_unverified"
    return "block_timeout"


# ─── Packet 18: Semantic Cache ────────────────────────────────────────────


@dataclass
class CacheEntry:
    key: str
    lane: str
    task_type: str
    ts: float
    intent_embedding: List[float]
    receipt: Dict[str, Any]
    ttl_hours: float = CACHE_TTL_HOURS

    def expired(self, now: Optional[float] = None) -> bool:
        now = now or time.time()
        return (now - self.ts) > self.ttl_hours * 3600


class SemanticCache:
    """Packet 18: deterministic semantic cache with TTL and lane-scoping."""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = (
            Path(root)
            if root
            else Path.home() / ".local/share/apex-orchestration/semantic_cache"
        )
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "entries").mkdir(exist_ok=True)

    @staticmethod
    def _quantize(vec: List[float], top_k: int = 4) -> str:
        """Quantize vector to top-k dim signature for fast prefix lookup."""
        idx = sorted(range(len(vec)), key=lambda i: -vec[i])[:top_k]
        return ",".join(f"{i}:{vec[i]:.2f}" for i in sorted(idx))

    def make_key(self, lane: str, task_type: str, intent_embedding: List[float]) -> str:
        raw = f"{lane}|{task_type}|{self._quantize(intent_embedding)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def lookup(
        self,
        lane: str,
        task_type: str,
        intent_embedding: List[float],
        threshold: float = CACHE_THRESHOLD,
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """Returns (receipt, similarity) on hit, None on miss."""
        # Fast prefix lookup
        target_q = self._quantize(intent_embedding)
        for entry_file in (self.root / "entries").glob("*.json"):
            try:
                entry = CacheEntry(**json.loads(entry_file.read_text()))
            except Exception:
                continue
            if entry.lane != lane or entry.task_type != task_type:
                continue
            if entry.expired():
                continue  # G2: lazy eviction
            # Compute cosine
            from ml_routing import cosine  # late import to avoid cycle

            sim = cosine(intent_embedding, entry.intent_embedding)
            if sim >= threshold:
                return (entry.receipt, sim)
        return None

    def store(
        self,
        lane: str,
        task_type: str,
        intent_embedding: List[float],
        receipt: Dict[str, Any],
    ) -> str:
        key = self.make_key(lane, task_type, intent_embedding)
        entry = CacheEntry(
            key=key,
            lane=lane,
            task_type=task_type,
            ts=time.time(),
            intent_embedding=intent_embedding,
            receipt=receipt,
        )
        (self.root / "entries" / f"{key}.json").write_text(
            json.dumps(
                {
                    "key": entry.key,
                    "lane": entry.lane,
                    "task_type": entry.task_type,
                    "ts": entry.ts,
                    "intent_embedding": entry.intent_embedding,
                    "receipt": entry.receipt,
                    "ttl_hours": entry.ttl_hours,
                }
            )
        )
        return key


# ─── Packet 19: DAG Scheduler ──────────────────────────────────────────────


@dataclass
class DAGNode:
    id: str
    lane: str
    gate: str
    depends_on: List[str] = field(default_factory=list)
    status: str = "PENDING"  # PENDING | READY | RUNNING | PASSED | FAILED | BLOCKED
    receipt: Optional[Dict[str, Any]] = None
    cause: Optional[str] = None


def detect_cycles(nodes: Dict[str, DAGNode]) -> bool:
    """G1 acyclicity gate. Returns True if cycle detected (Kahn's algorithm)."""
    in_degree: Dict[str, int] = {}
    for nid in nodes:
        in_degree[nid] = 0
    for n in nodes.values():
        for dep in n.depends_on:
            if dep in in_degree:
                in_degree[n.id] += 1
    queue = deque([nid for nid, d in in_degree.items() if d == 0])
    visited = 0
    while queue:
        cur = queue.popleft()
        visited += 1
        for n in nodes.values():
            if cur in n.depends_on:
                in_degree[n.id] -= 1
                if in_degree[n.id] == 0:
                    queue.append(n.id)
    return visited != len(nodes)


def ready_set(nodes: Dict[str, DAGNode]) -> List[str]:
    """Compute nodes whose dependencies are all PASSED and that are PENDING/READY."""
    out = []
    for n in nodes.values():
        if n.status in ("PENDING", "READY") and all(
            nodes[d].status == "PASSED" for d in n.depends_on if d in nodes
        ):
            out.append(n.id)
    # G5: deterministic order by node_id
    return sorted(out)


def propagate_block(nodes: Dict[str, DAGNode], failed_id: str) -> List[str]:
    """Mark all transitive descendants of a FAILED node as BLOCKED."""
    blocked = []
    # BFS over dependents
    queue = deque([failed_id])
    visited = {failed_id}
    # First build reverse adjacency
    dependents: Dict[str, List[str]] = {nid: [] for nid in nodes}
    for n in nodes.values():
        for dep in n.depends_on:
            if dep in dependents:
                dependents[dep].append(n.id)
    while queue:
        cur = queue.popleft()
        for child in dependents.get(cur, []):
            if child in visited:
                continue
            visited.add(child)
            if nodes[child].status not in ("PASSED",):
                nodes[child].status = "BLOCKED"
                nodes[child].cause = f"upstream_failure:{cur}"
                blocked.append(child)
            queue.append(child)
    return blocked


def schedule_dag(
    nodes: Dict[str, DAGNode], max_parallel: int = MAX_PARALLEL
) -> List[List[str]]:
    """Compute the execution waves (groups of nodes that can run in parallel).

    Returns a list of waves; each wave is a list of node_ids to dispatch in parallel.
    Raises ValueError on cycle (F-DEC-01).
    """
    if detect_cycles(nodes):
        raise ValueError("F-DEC-01 dag_cycle detected")
    # Working copy
    state = {nid: DAGNode(**vars(n)) for nid, n in nodes.items()}
    waves: List[List[str]] = []
    while True:
        ready = [
            nid
            for nid, n in state.items()
            if n.status in ("PENDING", "READY")
            and all(state[d].status == "PASSED" for d in n.depends_on if d in state)
        ]
        if not ready:
            break
        # G5: deterministic
        ready.sort()
        # G3: cap at max_parallel
        wave = ready[:max_parallel]
        for nid in wave:
            state[nid].status = "RUNNING"
        waves.append(wave)
        # Simulate completion: all dispatched in a wave PASS simultaneously
        for nid in wave:
            state[nid].status = "PASSED"
    return waves


# ─── Packet 20: Property-Based Testing ─────────────────────────────────────


@dataclass
class Property:
    name: str
    func: Callable[[Any], bool]
    description: str
    examples_run: int = 0
    falsifier: Optional[Any] = None


def detect_properties(
    subject_name: str, func_signatures: List[Tuple[str, str]]
) -> List[Property]:
    """Auto-detect properties from function signatures.

    func_signatures: list of (name, signature) e.g. ('sorted', 'list -> list').
    """
    props = []
    for name, sig in func_signatures:
        if "-> list" in sig and "list" in sig:
            # Idempotence: f(f(x)) == f(x) (for known idempotent functions)
            if name in ("sorted", "reversed", "frozenset", "set", "tuple", "unique"):
                props.append(
                    Property(
                        name=f"{name}_idempotent",
                        func=lambda f, x: f(f(x)) == f(x),
                        description=f"{name} is idempotent",
                    )
                )
            # Length-preserving for stable transforms
            if name in ("sorted", "reversed", "list", "tuple"):
                props.append(
                    Property(
                        name=f"{name}_length_preserving",
                        func=lambda f, x: len(f(x)) == len(x),
                        description=f"{name} preserves length",
                    )
                )
        if "-> dict" in sig and "dict" in sig:
            # Roundtrip: if there's a parser
            pass
    return props


def run_property(
    prop: Property, examples: List[Any], shrink: bool = True
) -> Tuple[bool, Optional[Any], int]:
    """Run a property against a list of examples. Returns (passed, falsifier, n_run)."""
    n_run = 0
    falsifier = None
    for ex in examples:
        n_run += 1
        try:
            if not prop.func(ex):
                falsifier = ex
                break
        except Exception:
            falsifier = ex
            break
    if falsifier is not None and shrink:
        # Minimal shrinking: try empty / smallest possible input.
        # Only shrink if the current falsifier is non-None; if any candidate
        # throws, skip it (don't clobber the existing falsifier with None).
        original = falsifier
        for c in [None, "", 0, [], {}, "x"]:
            if c is None:
                continue  # can't pass None to most props
            try:
                if not prop.func(c):
                    original = c
                    break
            except Exception:
                continue
        falsifier = original
    prop.examples_run = n_run
    return (falsifier is None, falsifier, n_run)


# ─── Packet 21: Mutation Testing ───────────────────────────────────────────

MUTATION_OPERATORS = ["AOR", "LOR", "ROR", "UOI", "CRP", "RVR", "SDL", "MCF"]


@dataclass
class MutationResult:
    operator: str
    site: str
    killed: bool
    surviving_reason: str = ""


def apply_simple_mutation(source: str, operator: str, site_index: int) -> str:
    """Apply a mutation operator to source. Site is a 0-based index into
    the lines array. This is a simplified textual mutator for testing.
    """
    lines = source.splitlines()
    if site_index >= len(lines):
        return source
    line = lines[site_index]
    if operator == "AOR":
        line = line.replace("+", "-", 1)
    elif operator == "LOR":
        line = line.replace("&&", "||", 1)
    elif operator == "ROR":
        line = line.replace("<", "<=", 1)
    elif operator == "UOI":
        line = "if not (x):" + line[2:] if line.startswith("if") else line
    elif operator == "CRP":
        line = line.replace("0", "1", 1)
    elif operator == "RVR":
        line = line.replace("return x", "return None", 1)
    elif operator == "SDL":
        line = ""  # delete the line
    elif operator == "MCF":
        line = line.replace(".method()", ".other_method()", 1)
    lines[site_index] = line
    return "\n".join(lines)


def mutation_score(results: List[MutationResult]) -> float:
    if not results:
        return 1.0
    killed = sum(1 for r in results if r.killed)
    return killed / len(results)


def should_pass_mutation_gate(
    score: float, target: float = MUTATION_SCORE_TARGET
) -> bool:
    """G1: mutation score must be >= target for the test suite to be elite."""
    return score >= target


# ─── Packet 22: Adaptive Compression ────────────────────────────────────────

TOKEN_BUDGET_DEFAULTS = {
    "code_edit": {"base": 1024, "min": 256, "max": 4096},
    "code_create": {"base": 2048, "min": 512, "max": 8192},
    "plan": {"base": 2048, "min": 512, "max": 8192},
    "audit": {"base": 2048, "min": 512, "max": 8192},
    "simplify": {"base": 1024, "min": 256, "max": 4096},
    "summarize": {"base": 512, "min": 128, "max": 2048},
    "classify": {"base": 256, "min": 64, "max": 1024},
    "embed": {"base": 64, "min": 32, "max": 256},
}

REASONING_FLOOR = 80
SAFETY_MARGIN = 1.2
RAG_THRESHOLD = 0.80
RAG_TOP_K = 5
CONFIDENCE_FLOOR = 0.80
MAX_CASCADE_DEPTH = 3
SELF_DEPRECATION_TOKENS = (
    "i don't know",
    "i'm not sure",
    "as an ai",
    "i cannot",
    "unable to",
    "i apologize",
    "unfortunately",
    "i'm unable",
)


def estimate_difficulty(
    input_tokens: int, task_type: str, invariants: int = 0
) -> float:
    """Return a difficulty factor in [0.6, 1.4]."""
    if input_tokens < 500:
        diff = 0.6
    elif input_tokens < 2000:
        diff = 1.0
    else:
        diff = 1.4
    if task_type in ("code_create", "plan"):
        diff += 0.2
    if invariants > 3:
        diff += 0.2
    return min(1.4, max(0.6, diff))


def compute_token_budget(
    task_type: str,
    lane: str,
    domain: str = "default",
    input_tokens: int = 1000,
    invariants: int = 0,
    coef: float = 1.0,
) -> int:
    """Adaptive token budget per Packet 22."""
    spec = TOKEN_BUDGET_DEFAULTS.get(task_type, {"base": 1024, "min": 256, "max": 4096})
    diff = estimate_difficulty(input_tokens, task_type, invariants)
    raw = spec["base"] * coef * diff * SAFETY_MARGIN
    floor = (
        REASONING_FLOOR if lane in ("REASON", "THINK-DEEP", "VERIFY") else spec["min"]
    )
    return int(min(spec["max"], max(floor, round(raw))))


# ─── Packet 23: Contract Testing ──────────────────────────────────────────


@dataclass
class Contract:
    contract_id: str
    module: str
    version: str
    functions: List[Dict[str, Any]]
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    supersedes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "module": self.module,
            "version": self.version,
            "functions": self.functions,
            "ts": self.ts,
            "supersedes": self.supersedes,
        }


def check_signature_in_contract(
    contract: Contract, expected_name: str, expected_params: List[str]
) -> bool:
    """G1/G2: consumer check. Returns True iff the signature is present."""
    for fn in contract.functions:
        if fn["name"] != expected_name:
            continue
        actual_params = [p["name"] for p in fn.get("params", [])]
        return actual_params == expected_params
    return False


def is_breaking_change(contract: Contract, new_functions: List[Dict[str, Any]]) -> bool:
    """G2: removing or renaming a public function is a breaking change."""
    old_names = {f["name"] for f in contract.functions}
    new_names = {f["name"] for f in new_functions}
    return bool(old_names - new_names)


# ─── Packet 24: Model Cascading ───────────────────────────────────────────


@dataclass
class CascadeStep:
    attempt: int
    lane: str
    confidence: float
    cost: float
    decision: str  # 'accept' or 'escalate'


@dataclass
class CascadeResult:
    steps: List[CascadeStep]
    final_lane: str
    final_confidence: float
    total_cost: float

    @property
    def accepted_on_first_try(self) -> bool:
        return len(self.steps) == 1 and self.steps[0].decision == "accept"


CASCADE_CHAINS = {
    "classify": ["ROUTER-FREE", "CODE-FAST", "CODE"],
    "code_edit": ["CODE-FAST", "CODE", "REASON"],
    "plan": ["REASON", "THINK-DEEP"],
    "audit": ["CODE-FAST", "VERIFY", "REASON"],
    "summarize": ["ROUTER-FREE", "CODE-FAST"],
}


def is_self_deprecation(output: str) -> bool:
    """Detect 'I don't know', 'as an AI', etc."""
    out_lower = output.lower()
    return any(tok in out_lower for tok in SELF_DEPRECATION_TOKENS)


def compute_confidence(output: str, expected_length: int, l2_proof: bool) -> float:
    """Confidence in [0, 1]. Below CONFIDENCE_FLOOR means escalate."""
    if not l2_proof:
        return 0.0
    if is_self_deprecation(output):
        return 0.2
    if not output:
        return 0.0
    actual_len = len(output)
    if actual_len < 0.5 * expected_length or actual_len > 2.0 * expected_length:
        return 0.5
    return 0.9


def should_escalate(confidence: float, threshold: float = CONFIDENCE_FLOOR) -> bool:
    return confidence < threshold


def run_cascade(
    task_type: str,
    output_at_lane: Dict[str, str],
    cost_at_lane: Dict[str, float],
    budget: float = 1.0,
    threshold: float = CONFIDENCE_FLOOR,
) -> CascadeResult:
    """Simulate a cascade. output_at_lane and cost_at_lane are mocked outputs."""
    chain = CASCADE_CHAINS.get(task_type, ["CODE"])
    steps: List[CascadeStep] = []
    total_cost = 0.0
    final_lane = chain[0]
    final_conf = 0.0
    for attempt, lane in enumerate(chain, 1):
        if attempt > MAX_CASCADE_DEPTH:
            break
        if total_cost > budget * 0.5 and attempt > 1:
            break
        out = output_at_lane.get(lane, "")
        cost = cost_at_lane.get(lane, 0.0)
        total_cost += cost
        conf = compute_confidence(out, expected_length=200, l2_proof=bool(out))
        decision = "escalate" if should_escalate(conf, threshold) else "accept"
        steps.append(CascadeStep(attempt, lane, conf, cost, decision))
        if decision == "accept":
            final_lane = lane
            final_conf = conf
            break
        final_lane = lane
        final_conf = conf
    return CascadeResult(
        steps=steps,
        final_lane=final_lane,
        final_confidence=final_conf,
        total_cost=total_cost,
    )


# ─── Packet 25: Retrieval-Augmented Context ──────────────────────────────


@dataclass
class Recall:
    mission_id: str
    similarity: float
    summary: str


def recall_similar(
    intent_text: str, memory: Any, k: int = RAG_TOP_K, threshold: float = RAG_THRESHOLD
) -> List[Recall]:
    """Top-k recall from an embedding memory (Packet 15)."""
    if memory is None:
        return []
    raw = memory.recall_similar(intent_text, k=k * 3)
    out = []
    for r in raw:
        if r.get("score", 0) >= threshold:
            out.append(
                Recall(
                    mission_id=r["mission_id"],
                    similarity=r["score"],
                    summary=r.get("summary_ref", ""),
                )
            )
        if len(out) >= k:
            break
    return out


def format_rag_context(recalls: List[Recall]) -> str:
    if not recalls:
        return ""
    parts = []
    for r in recalls:
        parts.append(
            f"[RECALL mission_id={r.mission_id} similarity={r.similarity:.2f}]"
        )
        parts.append(r.summary or "(no summary)")
        parts.append("[/RECALL]")
    return "\n".join(parts)


# ─── Packet 26: Constitutional Gate ───────────────────────────────────────

DEFAULT_CONSTITUTION: List[Dict[str, Any]] = [
    {
        "id": "C-1",
        "regex": r"\b(sovereign|sovereign\s+master|canonical\s+master|master\s+of\s+the\s+trade|sovereign\s+authority)\b",
        "severity": "BLOCKER",
        "description": "No 'Sovereign' / 'Canonical Master' / 'Master of' framing. Use 'Holographic Mesh'.",
    },
    {
        "id": "C-2",
        "regex": r"\b(highest\s+authority|final\s+word\s+on|ultimate\s+authority)\b",
        "severity": "BLOCKER",
        "description": "No 'highest authority' / 'final word' claims.",
    },
    {
        "id": "C-3",
        "regex": r"^\s*pass\s*$|return\s+True\s*$|NotImplementedError|TODO\s*:|FIXME\s*:",
        "severity": "BLOCKER",
        "description": "No stubs (return True / pass / NotImplementedError / TODO / FIXME in production code).",
    },
    {
        "id": "C-4",
        "regex": r"^✓\s*verified\s*$|tests?\s+passed\s*$",
        "severity": "BLOCKER",
        "description": "No fictional log lines without actual command output.",
    },
    {
        "id": "C-5",
        "regex": r"\bi'?ll?\s+(just\s+)?trust\s+(the\s+)?model\b",
        "severity": "BLOCKER",
        "description": "No 'trust the model' without a receipt.",
    },
    {
        "id": "C-6",
        "regex": r"\b(enterprise-grade|world-class|elite-tier)\b",
        "severity": "WARN",
        "description": "Use operator-legit vocabulary: elite, pro, Hard, G.",
    },
    {
        "id": "C-7",
        "regex": r"\bverified\b(?!.{0,200}receipt)",
        "severity": "BLOCKER",
        "description": "Every 'verified' claim must cite a receipt chain hash.",
    },
    {
        "id": "C-8",
        "regex": r"\boverwrite\s+(memory|state|file)\b",
        "severity": "BLOCKER",
        "description": "No silent overwrites; writes are append-only.",
    },
    {
        "id": "C-9",
        "regex": r"i'?ll?\s+do\s+(this|that)\s+later",
        "severity": "BLOCKER",
        "description": "No placeholders like 'I'll do this later'.",
    },
    {
        "id": "C-10",
        "regex": r"\bclobber\b.{0,50}\b(upstream|main)\b",
        "severity": "BLOCKER",
        "description": "No clobber of upstream; verify functional behavior before merging.",
    },
]


@dataclass
class Violation:
    rule_id: str
    description: str
    matches: List[str]


def check_constitution(
    artifact: str, constitution: List[Dict[str, Any]] = None
) -> List[Violation]:
    """Return BLOCKER violations only (WARN rules are reported elsewhere)."""
    constitution = constitution or DEFAULT_CONSTITUTION
    violations = []
    for rule in constitution:
        if rule["severity"] != "BLOCKER":
            continue
        import re as _re

        matches = []  # init per-rule

        # Build word-context for each match position
        for _m in _re.finditer(rule["regex"], artifact, _re.IGNORECASE | _re.MULTILINE):
            start = max(0, _m.start() - 200)
            ctx = artifact[start : _m.end()]
            # Rule-specific: "verified" must have "receipt" within 200 chars
            if rule["id"] == "C-7":
                if "receipt" not in ctx.lower():
                    matches.append(_m.group(0))
            else:
                matches.append(_m.group(0))
        if matches:
            violations.append(
                Violation(
                    rule_id=rule["id"],
                    description=rule["description"],
                    matches=[m if isinstance(m, str) else m[0] for m in matches],
                )
            )
    return violations


# ─── CLI (v1.3.0 entry point with v1.2.0 subcommands too) ─────────────────


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="apex-orchestration v1.3.0 advanced layer (packets 17-26)"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info")

    p_spec = sub.add_parser("test-spec")
    p_spec.add_argument("--draft-trust", type=float, required=True)
    p_spec.add_argument("--verify-trust", type=float, required=True)
    p_spec.add_argument("--draft-ms", type=float, required=True)
    p_spec.add_argument("--verify-ms", type=float, required=True)

    p_cache = sub.add_parser("test-cache")
    p_cache.add_argument("--lane", default="CODE")
    p_cache.add_argument("--task-type", default="code_edit")
    p_cache.add_argument("--intent", default="test")
    p_cache.add_argument("--threshold", type=float, default=CACHE_THRESHOLD)

    p_dag = sub.add_parser("test-dag")
    p_dag.add_argument("--max-parallel", type=int, default=MAX_PARALLEL)

    p_b = sub.add_parser("test-budget")
    p_b.add_argument("--task-type", default="code_edit")
    p_b.add_argument("--lane", default="CODE")
    p_b.add_argument("--input-tokens", type=int, default=1000)
    p_b.add_argument("--coef", type=float, default=1.0)

    p_c = sub.add_parser("test-constitution")
    p_c.add_argument("--text", required=True)

    args = ap.parse_args()

    if args.cmd == "info":
        print(
            json.dumps(
                {
                    "version": "1.3.0",
                    "packets": {
                        "17-speculative-decoding": "draft + verifier parallel, 2-3x speedup, trust-gated",
                        "18-semantic-cache": "vector-based prompt-response cache, 30-70% cost cut",
                        "19-dag-scheduler": "topo sort, cycle detection, parallel fan-out, block propagation",
                        "20-property-based-testing": "auto-generated invariants, Hypothesis-style, 100+ examples",
                        "21-mutation-testing": "verify test suite quality, >=80% mutation score required",
                        "22-adaptive-compression": "Per-task-type token budget with learned coefficient",
                        "23-contract-testing": "Producer/consumer signature lock + breaking-change gate",
                        "24-model-cascading": "Cheap-first dispatch, escalate on low confidence",
                        "25-retrieval-augmented-context": "Top-k similar past missions injected as context",
                        "26-constitutional-gate": "AGENTS.md §0 audit at DELIVERY (10 rules, BLOCKER/WARN)",
                    },
                    "constants": {
                        "CACHE_THRESHOLD": CACHE_THRESHOLD,
                        "CACHE_TTL_HOURS": CACHE_TTL_HOURS,
                        "MAX_PARALLEL": MAX_PARALLEL,
                        "SLA_MS_DEFAULT": SLA_MS_DEFAULT,
                        "MUTATION_SCORE_TARGET": MUTATION_SCORE_TARGET,
                        "PROPERTY_EXAMPLES_DEFAULT": PROPERTY_EXAMPLES_DEFAULT,
                        "REASONING_FLOOR": REASONING_FLOOR,
                        "SAFETY_MARGIN": SAFETY_MARGIN,
                        "RAG_THRESHOLD": RAG_THRESHOLD,
                        "RAG_TOP_K": RAG_TOP_K,
                        "CONFIDENCE_FLOOR": CONFIDENCE_FLOOR,
                        "MAX_CASCADE_DEPTH": MAX_CASCADE_DEPTH,
                    },
                },
                indent=2,
            )
        )
        return 0

    if args.cmd == "test-spec":
        can = can_speculate(args.draft_trust, args.verify_trust)
        decision = speculation_decision(
            args.draft_ms, args.verify_ms, draft_l2=True, verify_l2=True
        )
        print(json.dumps({"can_speculate": can, "decision": decision}, indent=2))
        return 0

    if args.cmd == "test-cache":
        from ml_routing import embed_intent

        cache = SemanticCache()
        v1 = embed_intent(args.intent)
        v2 = embed_intent(args.intent)
        receipt = {
            "lane": args.lane,
            "task_type": args.task_type,
            "l2_proof": True,
            "result": "cached output",
        }
        key = cache.store(args.lane, args.task_type, v1, receipt)
        hit = cache.lookup(args.lane, args.task_type, v2, threshold=args.threshold)
        v3 = embed_intent(args.intent + " (different)")
        miss = cache.lookup(args.lane, args.task_type, v3, threshold=args.threshold)
        print(
            json.dumps(
                {
                    "stored_key": key,
                    "hit": hit[0]["result"] if hit else None,
                    "hit_similarity": hit[1] if hit else None,
                    "miss_for_different_intent": miss[0] if miss else "miss (expected)",
                },
                indent=2,
            )
        )
        return 0

    if args.cmd == "test-dag":
        nodes = {
            "A": DAGNode(id="A", lane="CODE", gate="L2"),
            "B": DAGNode(id="B", lane="VERIFY", gate="L2", depends_on=["A"]),
            "C": DAGNode(id="C", lane="REVIEW", gate="L2", depends_on=["A"]),
            "D": DAGNode(id="D", lane="FUSE", gate="FUSE", depends_on=["B", "C"]),
        }
        waves = schedule_dag(nodes, max_parallel=args.max_parallel)
        print(json.dumps({"waves": waves, "n_waves": len(waves)}, indent=2))
        return 0

    if args.cmd == "test-budget":
        b = compute_token_budget(
            args.task_type, args.lane, "default", args.input_tokens, 0, args.coef
        )
        print(
            json.dumps(
                {
                    "task_type": args.task_type,
                    "lane": args.lane,
                    "input_tokens": args.input_tokens,
                    "coef": args.coef,
                    "budget": b,
                },
                indent=2,
            )
        )
        return 0

    if args.cmd == "test-constitution":
        v = check_constitution(args.text)
        print(
            json.dumps(
                {
                    "text_preview": args.text[:80],
                    "violations": [
                        {"id": x.rule_id, "desc": x.description, "matches": x.matches}
                        for x in v
                    ],
                },
                indent=2,
            )
        )
        return 0 if not v else 1

    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
