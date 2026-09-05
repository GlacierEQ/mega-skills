---
id: apex-mesh-dispatch
display_name: Apex Mesh Dispatch
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Apex Mesh Dispatch

## Purpose and selection

A code-producing mission needs a deterministic order of mesh lanes: reason first, then code, then verify, then review, then deliver. Use this Combo when the user wants a single non-trivial code task executed with full mesh coverage. Do not use it for trivial one-line edits, read-only research, or missions whose primary work is planning without code; route to `apex-orchestration` skill directly or to a domain-specific combo instead.

## Incremental value

This Combo does not duplicate the lower-layer methods. It takes the atomic `apex-orchestration` skill (which defines the mesh and the six lifecycle stages) and enforces a specific ordered route: REASON -> CODE -> VERIFY -> REVIEW -> DELIVER. It does not own the lane definitions, the receipt format, or the routing heuristics; those live in the skill.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `apex-orchestration` | skill | Yes | Provide mesh definitions, lifecycle, receipt format, routing rules | Mission mandate | INTAKE + DECOMPOSE stage receipts, DAG | 12 packets present, 12 lanes in mesh, 6 stages in lifecycle |
| 2 | `apex-orchestration` | skill | Yes | Execute DISPATCH: REASON first, then CODE / CODE-FAST | DAG, REASON plan | Subtask receipts for plan + code | Each subtask receipt has `l2_proof: true` and matching sha256 |
| 3 | `apex-orchestration` | skill | Yes | Execute VERIFY: VERIFY lane audits, REVIEW lane refines | Code subtask receipts | Auditor + refiner signatures | Three signatures present (producer, auditor, refiner) |
| 4 | `apex-orchestration` | skill | Yes | Execute FUSE + DELIVER: dedup, dominant-verified merge, delivery.json | Verified receipts | fused.json + delivery.json with SHIPPED status | chain_hash reproducible, memory_write_id present |

## Ordered execution

1. **INTAKE + DECOMPOSE — `apex-orchestration` (packets 01, 02, 04)** consumes Mission mandate, produces `intake.json` and `dag.json`, and verifies scope + DAG have no cycles.
2. **DISPATCH — `apex-orchestration` (packets 01, 03, 04, 11)** consumes `dag.json`, produces subtask receipts from REASON and CODE lanes, and verifies each receipt has `l2_proof: true` with matching `sha256`.
3. **VERIFY — `apex-orchestration` (packets 03, 05)** consumes code receipts, produces auditor (VERIFY lane) and refiner (REVIEW lane) signatures, and verifies all three signatures are present.
4. **FUSE + DELIVER — `apex-orchestration` (packets 06, 07, 08, 12)** consumes verified receipts, produces `fused.json` and `delivery.json` with status `SHIPPED`, and verifies `chain_hash` is reproducible and `memory_write_id` is present.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `apex-orchestration` (INTAKE) | `apex-orchestration` (DISPATCH) | intake.json, dag.json | First subtask receipts | INTAKE owner | DAG has no cycles, every node names a lane and a gate |
| `apex-orchestration` (DISPATCH) | `apex-orchestration` (VERIFY) | Subtask receipts with `l2_proof: true` | Auditor + refiner signatures | DISPATCH owner | Three signatures present for every code subtask |
| `apex-orchestration` (VERIFY) | `apex-orchestration` (FUSE) | Verified receipts (all signatures) | fused.json | VERIFY owner | No draft input, conflict resolution logged |
| `apex-orchestration` (FUSE) | `apex-orchestration` (DELIVER) | fused.json | delivery.json with status SHIPPED | FUSE owner | chain_hash reproducible, memory_write_id present |

## Evidence, risks, and state

The Combo must record `audit.jsonl`, `token_log.jsonl`, `routing_decisions.jsonl`, `receipts/*.json`, `fused.json`, `delivery.json` in `runs/<mission_id>/`. It must not cross security boundary (Packet 10), exceed token budget (Packet 11), or advance a stage without L2 evidence (Packet 02). Update `runs/<mission_id>/` after each stage transition; persist to memory (Packet 08) at DELIVERY.

## Quality gates

The Combo is complete only when all 12 packets are present in `apex-orchestration/packets/`, the 3 JSON-Schema files validate, every code subtask has three signatures, the receipt chain hash is reproducible, the delivery status is `SHIPPED` and `memory_write_id` is recorded. The next layer (mega-skill `apex-orchestrator-mesh`) can consume `delivery.json` without relying on raw conversation history.

## Compound output

**Artifact:** `delivery.json` containing the verified compound artifact, three signatures, `receipt_chain_sha256`, and `memory_write_id`.

**Ready for Mega Skill integration when:**

1. All 12 packets of `apex-orchestration` are present at version >= 1.0.0.
2. Every dispatched subtask returned a receipt with `l2_proof: true`.
3. Three-signature rule was enforced for every code subtask.
4. `fused.json` deterministic (re-running produces identical chain hash).
5. `delivery.json` has status `SHIPPED` and `memory_write_id` is queryable.
