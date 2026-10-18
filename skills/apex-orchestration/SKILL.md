---
name: apex-orchestration
description: "Complete APEX operational framework. Holographic Mesh Orchestrator across 12 free-model lanes, six-stage mission lifecycle, receipt-chain verification, 26 production-grade logic packets (12 base + 4 ML/self-improving + 5 cutting-edge dev techniques + 5 elite hardening). Use when executing APEX workflows, dispatching multi-model missions, fusing verified outputs, online-learning, speculative decoding, semantic caching, DAG scheduling, property-based testing, mutation testing, adaptive token compression, contract testing, model cascading, retrieval-augmented context, or constitutional gate."
schema: ../../schemas/combo-skill.schema.json
version: 1.3.1
status: active
---

# APEX Orchestration v1.0.0 — Holographic Mesh

**One source of truth** for orchestration across the APEX stack. The operator (mesh) agent, the combo-skill, and the mega-skill all reference this document. Adding or changing mesh semantics happens here, in the versioned packets, never in the derived layers.

---

## Architecture

```
APEX MESH (Holographic, 12 lanes, free-tier)
├── 12 Logic Packets           — canonical contracts (this skill/packets/)
├── Mission Lifecycle          — INTAKE → DECOMPOSE → DISPATCH → VERIFY → FUSE → DELIVER
├── Receipt Format             — JSON-Schema-locked, sha256-chained
├── Routing Heuristics         — 8 ordered rules, 5 hard gates
├── Verification Gate          — L2 minimum, 7-level ladder, three-signature rule
├── FUSE Policy                — deterministic merge, dominant-verified evidence
├── Delivery Contract          — closed-set status, one artifact, one chain
├── Memory Persistence         — append-only, provenance-required, queryable
├── Failure Modes              — 13 closed codes, every failure has an owner
├── Security Boundary          — default-deny, blast-radius, secret-scan
├── Token Economy              — cache-hit, surgical injection, budget gate
└── Observability              — append-only logs, replayable, inspectable
```

---

## Token-Aware Depth Law — Above Compression, Not Instead of It

Canonical source: https://github.com/GlacierEQ/aspen-grove-core/blob/main/TOKEN_AWARE_EXECUTION.md

The Aspen doctrine decides **how much useful depth the mission deserves**. Packet 11 (Token Economy) and Packet 22 (Adaptive Compression) then optimize cost and context waste inside that depth allocation. They must never silently turn cost optimization into objective minimization.

Before DECOMPOSE/DISPATCH, scale reasoning, context, tool, and verification effort with:
- mission **criticality**;
- context/dependency surface;
- uncertainty and ambiguity;
- executable opportunity;
- **verification burden**;
- compounding/reuse value;
- remaining frontier size.

**Depth is not verbosity.** Prefer source recovery, dependency reasoning, code/tool execution, adversarial tests, provider readback, and receipts over repeated explanation. If further reasoning no longer changes the route, execute. A successful lane or packet is a checkpoint, not an automatic mission stop. Continue until **the executable frontier is exhausted**, a genuine external dependency blocks, or marginal work has sharply diminishing value.

Derived skills and workers reference this canonical Aspen doctrine; they do not duplicate its full text or invent competing token-allocation laws.

---

## 1. The 26 Logic Packets (canonical)

| # | Packet | Purpose | Source-of-truth for |
|---|--------|---------|---------------------|
| 01 | `01-mesh-definition.md` | Names every lane, model, predicate, output contract | COMBO + MEGA routing |
| 02 | `02-mission-lifecycle.md` | Six-stage state machine with L2 evidence gates | Every mission |
| 03 | `03-receipt-format.md` | JSON-Schema for subtask receipts | FUSE + DELIVERY |
| 04 | `04-routing-heuristics.md` | 8 ordered rules, 5 hard gates | DECOMPOSE |
| 05 | `05-verification-gate.md` | L2 minimum, three-signature rule, 7-level ladder | VERIFY stage |
| 06 | `06-fuse-policy.md` | Deterministic merge, dedup, conflict resolution | FUSE stage |
| 07 | `07-delivery-contract.md` | Closed status set, one artifact, receipt chain | DELIVERY stage |
| 08 | `08-memory-persistence.md` | Append-only memory writes, provenance required | cross-session state |
| 09 | `09-failure-modes.md` | 13 failure codes, owners, recovery | any failure |
| 10 | `10-security-boundary.md` | Default-deny, blast-radius, secret-scan | every action |
| 11 | `11-token-economy.md` | Budget, cache-hit, max_tokens floors | every dispatch |
| 12 | `12-observability.md` | Append-only logs, replay, inspect | every mission |
| 13 | `13-ml-routing.md` | Learned scoring function for routing (6-component) | DECOMPOSE (within hard-rule set) |
| 14 | `14-receipt-mining.md` | Online pipeline: receipts → lane_stats + anti-patterns | DELIVERY → state update |
| 15 | `15-embedding-memory.md` | Intent-embedding memory of every delivered mission | INTAKE / DECOMPOSE recall |
| 16 | `16-self-improving-loop.md` | Hebbian update with regression gate + watchdog | after every mission |
| 17 | `17-speculative-decoding.md` | Draft + verifier parallel, 2-3× speedup, trust-gated | DISPATCH latency optimization |
| 18 | `18-semantic-cache.md` | Vector-based prompt-response cache, 30-70% cost cut | DISPATCH (before any lane call) |
| 19 | `19-dag-scheduler.md` | Topo sort, cycle detection, parallel fan-out, block propagation | DISPATCH (graph execution) |
| 20 | `20-property-based-testing.md` | Auto-generated invariants, 100+ examples, shrunk counterexamples | VERIFY (deep quality) |
| 21 | `21-mutation-testing.md` | Verify test suite quality, ≥80% mutation score required | VERIFY (test strength) |
| 22 | `22-adaptive-compression.md` | Per-task-type token budget with learned coefficient | DISPATCH (cost optimization) |
| 23 | `23-contract-testing.md` | Producer/consumer signature lock + breaking-change gate | VERIFY (API contracts) |
| 24 | `24-model-cascading.md` | Cheap-first dispatch, escalate on low confidence | DISPATCH (cost-quality tradeoff) |
| 25 | `25-retrieval-augmented-context.md` | Top-k similar past missions injected as context | INTAKE / DECOMPOSE (memory recall) |
| 26 | `26-constitutional-gate.md` | AGENTS.md §0 audit at DELIVERY (10 rules, BLOCKER/WARN) | DELIVERY (final safety net) |

Each packet is a self-contained markdown file in `packets/` with:
- An **Invariant** (L5) — the law that must hold.
- **Gates** — closed-set rules with `G#` IDs.
- **Anti-patterns** — closed-set refusals.
- **L2 Evidence** — what proof is required to ship the packet.
- **Versioning** — how the packet changes.

---

## 2. The Mesh (12 lanes)

The orchestrator itself is lightweight (`nemotron-3.5-lightning:free` for routing speed). Heavy work goes to specialist lanes. Pick by capability, not by familiarity.

| Lane | Model | When | Output |
|------|-------|------|--------|
| REASON | `nvidia/nemotron-3-ultra-550b-a55b:free` | Hard planning, multi-invariant, cross-domain synthesis | `plan.md` with Invariants, DAG, Risks |
| CODE | `poolside/laguna-s-2.1:free` | Code generation, refactor, bug fix | `{files, sha256, tests, l2_proof}` |
| CODE-FAST | `poolside/laguna-xs-2.1:free` | Sub-agent code, narrow scope | `{files, sha256, l2_proof}` |
| VERIFY | `z-ai/glm-5.2:free` | Adversarial audit, demand proof | `{findings, severity_counts, approve\|reject}` |
| REVIEW | `cohere/north-mini-code:free` | Style, DRY, dead code | `{diff, complexity_before, complexity_after}` |
| LONG-CTX | `thinkingmachines/inkling:free` | >500k token reads, full-codebase audits | `{summary, citations[]}` |
| LONG-CTX-ALT | `minimax/minimax-m3:free` | Long-ctx fallback | `{summary, citations[]}` |
| THINK-DEEP | `minimax/minimax-m2.7:free` | Long-horizon planning, evolution | `{decomposition, evolution_log[]}` |
| NANO-PERCEPTION | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Image / video / audio input | `{structured_perception}` |
| DOMAIN-MED | `inclusionai/ling-3.0-flash-sante:free` | Medical / clinical only | `{answer, caveats, source_ids[]}` |
| DOMAIN-FIN | `inclusionai/ling-3.0-flash-fin:free` | Finance / quantitative only | `{answer, caveats, source_ids[]}` |
| ROUTER-FREE | `openrouter/free` | Smoke tests, low-stakes | `{response}` (always re-verified) |

Full predicates, output contracts, and gates in **Packet 01**.
Routing rules in **Packet 04**.

---

## 3. Mission Lifecycle (six stages)

```
INTAKE  ->  DECOMPOSE  ->  DISPATCH  ->  VERIFY  ->  FUSE  ->  DELIVER
   |          |            |          |         |        |
 receipt-A   dag.json   receipts[]  proofs[]  fused   delivery.json
```

Each stage has entry/exit conditions, an L2 evidence requirement, and a failure owner. Skipping a stage is a FUSE rejection. Full contracts in **Packet 02**.

---

## 4. Receipt Format (canonical)

Every dispatched subtask returns a receipt conforming to `schemas/receipt.schema.json`:

```json
{
  "lane": "CODE",
  "model": "poolside/laguna-s-2.1:free",
  "task": "<one-line>",
  "files_changed": ["path/a.ts"],
  "sha256": ["<64 hex>"],
  "tests": {"cmd": "npm test", "exit": 0, "summary": "47 passed"},
  "duration_ms": 12340,
  "l2_proof": true,
  "parent_mission_id": "mission_<ulid>"
}
```

`l2_proof: true` is the bar. A receipt without it is a draft, never a deliverable. Full schema and chain hash in **Packet 03**.

---

## 5. Three-Signature Rule (code)

Every code subtask collects three independent signatures before FUSE:

| Order | Role | Lane | Produces |
|------:|------|------|----------|
| 1 | Producer | CODE / CODE-FAST | `{files, sha256, tests, l2_proof}` |
| 2 | Auditor | VERIFY | `{findings, severity_counts, approve\|reject}` |
| 3 | Refiner | REVIEW | `{diff, complexity_before, complexity_after}` |

Missing signature = FUSE block. Full rules in **Packet 05**.

---

## 6. Routing Heuristics (8 rules, ordered)

1. **R-MEDICAL** → DOMAIN-MED (hard gate)
2. **R-FINANCE** → DOMAIN-FIN (hard gate)
3. **R-MULTIMODAL** → NANO-PERCEPTION (hard gate)
4. **R-LONGCTX** → LONG-CTX (input > 500k tokens, hard gate)
5. **R-PLAN** → REASON (plans, multi-invariant, cross-domain, hard gate)
6. **R-CODE-EDIT** → CODE (default for code)
7. **R-CODE-FAST** → CODE-FAST (subagent, < 200 lines)
8. **R-DEFAULT** → ROUTER-FREE (smoke) + VERIFY (audit)

First match wins. Domain rules cannot be overridden. Full table in **Packet 04**.

---

## 7. Core Law

- **Holographic mesh over single-winner.** No model carries the whole load. Every non-trivial mission touches two or more lanes.
- **Verify before claim.** Receipts, SHA-256, test green, diff read. Proof, not prose.
- **Zero stubs.** No `return True`, no `pass`, no "I will do this later." Ship or refuse.
- **Elite vocabulary, no embellishment.** Lead with the work, not the doctrine.

---

## Usage Triggers

- "execute mission", "dispatch to mesh", "fuse outputs"
- "open packet 0X", "what's in packet N"
- "validate packet", "check signature"
- "ship / block / refuse", "what's the status"
- "route to lane", "swap lane", "lane health"

---

## Derived Layers

This skill is the canonical source. Two derived layers exist:

- **Combo Skill** `apex-mesh-dispatch` — orders REASON → CODE → VERIFY → REVIEW → DELIVER.
- **Mega Skill** `apex-orchestrator-mesh` — full mission system with state, gates, durable handoff.

Both must reference, not duplicate, this skill's content.
