# Packet 08 — MEMORY-PERSISTENCE

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Cryptographic chain across sessions, queryable, evictable, never overwritten"
**Layer:** Skill
**Scope:** How orchestrator state crosses session boundaries. Memory writes are part of the receipt chain, not side effects.

---

## Invariant (L5)

A memory write is valid iff:

1. `key`, `value`, and `tags` are all present and well-typed.
2. `ts` is ISO8601 UTC.
3. `provenance` block records which mission produced the write.
4. The `memory_write_id` is returned by the memory backend and recorded.
5. Writes are **append-only**; updates create new versions, never overwrite.

## Memory Schema (canonical)

```json
{
  "memory_write_id": "mem_<ulid>",
  "mission_id": "mission_<ulid>",
  "ts": "2026-09-04T13:35:50Z",
  "key": "mission:mission_...",
  "value": { ... },
  "tags": ["apex", "delivered", "..."],
  "provenance": {
    "operator_model": "nvidia/nemotron-3.5-lightning:free",
    "lane_chain": ["REASON", "CODE", "VERIFY", "REVIEW"],
    "receipt_chain_sha256": "...",
    "session_id": "ses_..."
  },
  "version": 1,
  "supersedes": null
}
```

## What Gets Persisted

| Event | What | Key prefix |
|-------|------|------------|
| INTAKE complete | scope, blast radius, classification | `intake:` |
| DECOMPOSE complete | DAG hash | `dag:` |
| DISPATCH each node | subtask receipt | `subtask:` |
| VERIFY each node | verifier receipt | `verify:` |
| FUSE complete | compound artifact hash, dedup count, conflict count | `fuse:` |
| DELIVER complete | full delivery.json (truncated) + receipt_chain_sha256 | `mission:` |
| BLOCKED / REFUSED | cause, remediation | `block:` / `refuse:` |

## What Does NOT Get Persisted

- Raw model outputs longer than 4 KB. Summarize and link.
- Credentials, tokens, PII (never, per ownership rules).
- Inferred user intent outside the explicit mandate.

## Gates

- **G1 — Provenance required.** Every write has a `provenance` block. No anonymous writes.
- **G2 — Chain hash required.** `receipt_chain_sha256` ties the write to its mission's audit trail.
- **G3 — Version gate.** Updates create `version: N+1` and set `supersedes: <prev_id>`. No silent overwrite.
- **G4 — Eviction gate.** Eviction only by explicit user command or 90-day TTL. Memory is not silently pruned.

## Anti-Patterns

- Writing the full conversation to memory.
- Writing model outputs without provenance.
- Overwriting a previous write with new content.
- Evicting memory to "save space."

## L2 Evidence

- Backend returns a `memory_write_id` per write.
- Each write is queryable by `mission_id`, `tags`, or `key` prefix.
- Drift test: writes for a given `mission_id` are reproducible from the receipt chain.

## Versioning

- Major bump: change to schema, change to provenance requirements.
- Minor bump: new optional field.

Current version: **1.0.0**
