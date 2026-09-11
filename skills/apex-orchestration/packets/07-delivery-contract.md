# Packet 07 — DELIVERY-CONTRACT

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "One artifact, one status line, one receipt chain"
**Layer:** Skill
**Scope:** The shape of a final delivery. What DELIVER hands to the user and what gets persisted to memory.

---

## Invariant (L5)

A delivery is valid iff:

1. There is exactly one compound artifact (no orphans).
2. There is exactly one status line from the closed set `{SHIPPED, BLOCKED, REFUSED}`.
3. The receipt chain hash is reproducible from the staged receipts.
4. The memory write is recorded with a `memory_write_id` and is queryable.
5. `SHIPPED` includes run-quality evidence proving source coverage, a direct mission delta, durable outputs, verification, and an exact next frontier.

## Status Vocabulary (closed set)

| Status | When | Cause field | User gets |
|--------|------|-------------|-----------|
| SHIPPED | all six stages passed; FUSE produced a verified compound | n/a | artifact + receipt chain |
| BLOCKED | a gate failed but the mission is still reachable (e.g. quota, missing input) | required | failure owner + remediation |
| REFUSED | the mission is invalid by doctrine (e.g. illegal, out-of-scope, unverifiable) | required | reason + redirect |

A delivery is never `OK`, `DONE`, `SUCCESS`, or any other fuzzy term. Closed set.

## Required Fields in `delivery.json`

```json
{
  "mission_id": "mission_<ulid>",
  "status": "SHIPPED | BLOCKED | REFUSED",
  "compound_artifact": { ... },                       // one and only one
  "status_line": "single line, max 240 chars",
  "receipt_chain_sha256": "<64 hex>",
  "signatures": {
    "producer":   { "lane": "...", "ts": ..., "sha256": "..." },
    "auditor":    { "lane": "...", "ts": ..., "sha256": "..." },
    "refiner":    { "lane": "...", "ts": ..., "sha256": "..." }
  },
  "memory_write_id": "mem_<ulid>",
  "run_quality": {                                  // required when status == SHIPPED
    "source_coverage": {"scope": "bounded | partial | exhaustive", "evidence": ["..."]},
    "mission_delta": {"changed": true, "before": "...", "after": "..."},
    "durable_outputs": ["repo:path-or-provider-receipt"],
    "verification": {"status": "verified", "evidence": ["..."]},
    "next_frontier": "exact executable continuation point"
  },
  "causes": [],                                       // present iff status != SHIPPED
  "ts": "<ISO8601 UTC>"
}
```

## Memory Write

Every SHIPPED delivery is written to memory with:

- `key = "mission:" + mission_id`
- `value = {summary, artifact_path, receipt_chain_sha256}`
- `tags = ["apex", "delivered", <domain_tag>]`

The `memory_write_id` is returned by the memory backend and recorded in `delivery.json`.

## Gates

- **G1 — One-artifact gate.** The compound artifact is exactly one. Multiple artifacts require multiple deliveries, not one big one.
- **G2 — Status closed-set gate.** Status must be in the closed vocabulary. Anything else is REFUSED.
- **G3 — Memory-write gate.** SHIPPED without `memory_write_id` is BLOCKED, not SHIPPED.
- **G4 — Reproducibility gate.** Same mission inputs and same staged receipts must produce the same `receipt_chain_sha256`.
- **G5 — Mission-delta gate.** `SHIPPED` is invalid unless `run_quality.mission_delta.changed == true` with explicit before/after state.
- **G6 — Source-coverage gate.** Exhaustive review may be claimed only when `source_coverage.scope == exhaustive` and coverage evidence is recorded; partial retrieval remains partial.
- **G7 — Verification/frontier gate.** `SHIPPED` requires verification evidence, at least one durable output, and an exact next executable frontier.

## Anti-Patterns

- "Done!" or "All set!" as status line.
- Two artifacts in one delivery.
- SHIPPED without persisting to memory.
- SHIPPED because a plan, summary, heartbeat, or token mutation exists but no direct mission delta is recorded.
- Calling partial retrieval exhaustive or omitting coverage evidence.
- BLOCKED without a cause.

## L2 Evidence

- `delivery.json` is itself a receipt.
- Memory backend returns a queryable `memory_write_id`.
- Receipt chain is reproducible.

## Versioning

Adding a status to the closed set is a major bump. Adding a field is a minor bump.

Current version: **1.1.0**
