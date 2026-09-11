# Packet 09 — FAILURE-MODES

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Closed taxonomy, every failure has an owner, every failure is recoverable or refused"
**Layer:** Skill
**Scope:** All known failure modes, their detection, their owner, and their recovery.

---

## Invariant (L5)

Every failure is either:

- **Recoverable**: re-dispatch with a new branch and updated DAG.
- **Refusable**: the mission is invalid or unverifiable; delivery is REFUSED.

No silent failure. No "we'll figure it out." No third category.

## Failure Taxonomy (closed set)

| Code | Name | Stage | Detection | Owner | Default Resolution |
|------|------|-------|-----------|-------|-------------------|
| F-INT-01 | scope_ambiguous | INTAKE | classification confidence < 0.6 | operator | ask one question, BLOCK until answered |
| F-INT-02 | budget_exceeded | INTAKE | estimated cost > mission.budget | operator | BLOCK with cost breakdown, user can raise budget |
| F-DEC-01 | dag_cycle | DECOMPOSE | DAG contains a cycle | operator | refuse DAG, re-decompose |
| F-DEC-02 | lane_unavailable | DECOMPOSE | selected lane is unhealthy | operator | swap to fallback (same role) |
| F-DIS-01 | dispatch_timeout | DISPATCH | no receipt within `lane_timeout_ms` | orchestrator | re-dispatch once, then BLOCK |
| F-DIS-02 | quota_exhausted | DISPATCH | lane reports quota exhausted | orchestrator | BLOCK mission, do not retry |
| F-VER-01 | l2_proof_missing | VERIFY | receipt lacks l2_proof or sha256 mismatch | operator | re-dispatch, do not advance |
| F-VER-02 | three_sig_missing | VERIFY | code subtask missing auditor or refiner signature | operator | re-dispatch missing signature only |
| F-FUSE-01 | draft_input | FUSE | any input receipt has l2_proof != true | operator | drop drafts, BLOCK if nothing left |
| F-FUSE-02 | conflict_unresolved | FUSE | conflict could not be resolved by evidence | operator | BLOCK with both options, user decides |
| F-DEL-01 | memory_write_failed | DELIVERY | memory backend did not return id | operator | BLOCK; retry once; then REFUSE |
| F-DEL-02 | chain_hash_drift | DELIVERY | receipt chain hash != reproducible | operator | REFUSE; mission is untrustworthy |
| F-DEL-03 | run_quality_invalid | DELIVERY | SHIPPED lacks valid source coverage, changed mission delta, durable output, verification evidence, or exact next frontier | operator | BLOCK; strengthen evidence and retry |

## Detection Ladder

| Detector | Where | What it watches |
|----------|-------|-----------------|
| watchdog | runtime | dispatch timeouts, missing callbacks |
| health probe | runtime | lane health, quota, rate limits |
| receipt validator | FUSE | sha256 drift, l2_proof missing, schema violations |
| chain hash | DELIVERY | chain_hash reproducibility |
| memory probe | DELIVERY | write success |

## Gates

- **G1 — Closed-set gate.** A failure code outside this taxonomy is a defect; reject and log.
- **G2 — Owner gate.** Every failure has exactly one owner. If two owners claim, the earlier stage wins.
- **G3 — Recovery gate.** Recoverable failures are retried at most once. Two retries = BLOCK.
- **G4 — Refusal gate.** REFUSED is forever. Re-issue the mission with a new mission_id.

## Anti-Patterns

- Silently retrying forever.
- Skipping a failure to "stay on schedule."
- Marking a failure as "known issue" without owner and recovery path.

## L2 Evidence

- Every failure produces a `failure.json` with: code, stage, owner, evidence, recovery attempt count, ts.
- Failures are persisted to memory with key `failure:<mission_id>:<code>`.

## Versioning

- Major bump: new failure code that changes ownership.
- Minor bump: new failure code with default resolution.

Current version: **1.0.0**
