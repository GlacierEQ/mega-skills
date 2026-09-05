# Packet 24 — MODEL-CASCADING

**Owner:** apex-orchestration v1.3.0
**Maturity:** 9 / "Try cheap first, escalate only if confidence is low; 40-70% spend cut on well-bounded tasks"
**Layer:** Skill
**Scope:** When a task has a well-defined verification gate, the orchestrator tries a cheap lane first. If the cheap lane's output is uncertain (low confidence score), escalate to a more expensive lane for one more attempt.

---

## Invariant (L5)

A cascading dispatch is valid iff:
1. At least 2 lanes are tried in cascade order: cheap → expensive.
2. The cheap lane's output is `uncertain` (confidence < threshold) → escalate.
3. The cascade depth is bounded: `MAX_CASCADE_DEPTH = 3` (cheap → mid → expensive).
4. Each escalation step's receipt is preserved (audit trail).
5. The final output is the highest-confidence receipt.

## The Confidence Score

A cheap lane's output is `uncertain` if any of:
- `l2_proof == false`
- The output's `length` is more than 2x or less than 0.5x the expected length for the task_type.
- The output contains a self-deprecation token (e.g. "I don't know", "I'm not sure", "as an AI").
- A structural check fails (e.g. code doesn't parse for `code_*` tasks).

## Cascade Definitions

| Task type | Cascade chain |
|---|---|
| `classify` | ROUTER-FREE → CODE-FAST → CODE |
| `code_edit` | CODE-FAST → CODE → REASON |
| `plan` | REASON → THINK-DEEP (no further) |
| `audit` | CODE-FAST → VERIFY → REASON |
| `summarize` | ROUTER-FREE → CODE-FAST (no further) |

## Gates

- **G1 — Depth gate.** MAX_CASCADE_DEPTH = 3. After 3 attempts, return the best of the 3.
- **G2 — Confidence gate.** If the cheap lane's confidence >= `CONFIDENCE_FLOOR` (default 0.80), skip escalation. No cascade.
- **G3 — Cost gate.** Track cumulative tokens. If `cost_so_far > budget * 0.5`, halt cascade and return the best so far.
- **G4 — Audit gate.** Every cascade step is logged in `runs/<mission_id>/cascade_log.jsonl` with `(attempt, lane, confidence, cost, decision)`.
- **G5 — No-regression gate.** If the cascade escalates, the final output is **never** worse than the cheap output — measured by L2 proof, structural validity, or human-eval signal.

## Anti-Patterns

- Cascading for every task (cascading is for well-bounded tasks only; vague tasks need REASON first).
- Skipping the cheap lane because the orchestrator "knows" the task is hard (the cheap lane may surprise).
- Escalating past MAX_CASCADE_DEPTH (cost explosion).
- Returning a non-L2 output from a cascade step (must have L2 proof for the chosen output).

## L2 Evidence

- Depth test: cascade halts at MAX_CASCADE_DEPTH.
- Confidence test: cheap lane with confidence 0.85 → no escalation.
- Cost test: cumulative cost > budget * 0.5 → halt.
- No-regression test: final output's L2 proof is true.
- Cascade-log test: every step has (lane, confidence, cost, decision).

## Versioning

- **Major bump:** MAX_CASCADE_DEPTH change, confidence floor change.
- **Minor bump:** new task_type cascade chain added.
- **Patch:** bug fix.

Current version: **1.0.0** (paired with apex-orchestration v1.3.0).
