# Packet 02 — MISSION-LIFECYCLE

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Six-stage state machine with L2 evidence at every transition"
**Layer:** Skill
**Scope:** Canonical stages a mission must pass. Each stage has an entry condition, an exit condition, an L2 evidence requirement, and a failure owner.

---

## Invariant (L5)

A mission is valid iff it passes through all six stages in order, with L2 evidence recorded at each transition. Skipping a stage = FUSE rejection.

## Stages (state machine)

```
INTAKE -> DECOMPOSE -> DISPATCH -> VERIFY -> FUSE -> DELIVER
   |          |           |          |        |        |
   v          v           v          v        v        v
 receipt-A  receipt-B  receipt-C  receipt-D  receipt-E  receipt-F
```

| Stage | Entry Condition | Exit Condition | L2 Evidence | Failure Owner |
|-------|-----------------|----------------|-------------|---------------|
| INTAKE | user mandate received | scope + budget + blast-radius declared | `intake.json` {mission_id, scope, budget, blast_radius, classification} | operator |
| DECOMPOSE | intake valid | DAG built; every node names lane, gate, receipt | `dag.json` {nodes[], edges[], gates[]} | operator |
| DISPATCH | dag valid | every node dispatched with receipt-C or BLOCKED | `{receipts[]}` per node | orchestrator |
| VERIFY | dispatch complete | every node has L2 proof OR re-dispatched | `{proofs[], re_dispatches[]}` | VERIFY lane |
| FUSE | all verified | one compound artifact, no orphan lanes, conflicts resolved | `fused.json` {artifacts, dedup_count, conflicts_resolved} | operator |
| DELIVER | fused valid | one artifact, one status line, one receipt chain, memory persisted | `delivery.json` {artifact, status, receipt_chain_sha256, memory_write_id} | operator |

## Gates

- **G1 — Re-entry forbidden.** A stage may not be re-entered once exited; re-dispatch is a new branch, not a rollback.
- **G2 — Evidence before advance.** Cannot advance from stage N to N+1 without L2 evidence for stage N.
- **G3 — Budget gate at DISPATCH.** If estimated cost > mission.budget, mission is BLOCKED with cost breakdown.

## Anti-Patterns

- Skipping INTAKE because the request "looks obvious".
- Skipping FUSE because outputs "seem aligned".
- Calling DELIVER before FUSE; calling VERIFY before DISPATCH.

## L2 Evidence

`receipts/*.json` — one per stage, named `{mission_id}-{stage}.json`, schema in `schemas/stage-receipt.schema.json`.

## Versioning

Stages are stable. Adding a sub-stage is a minor bump. Removing a stage is forbidden (would break existing audit trails).

Current version: **1.0.0**
