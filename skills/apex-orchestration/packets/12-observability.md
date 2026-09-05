# Packet 12 — OBSERVABILITY

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Every action observable, every state queryable, no silent state"
**Layer:** Skill
**Scope:** Logs, metrics, traces, and inspection surface for the orchestrator.

---

## Invariant (L5)

Every state mutation is observable iff:

1. It is logged in a structured append-only file.
2. It is queryable by `mission_id`, `lane`, `stage`, or `ts`.
3. Logs and metrics can be replayed to reconstruct mission state.
4. There is no "internal state" that is not also on disk.

## Logging Surfaces

| File | Format | Purpose |
|------|--------|---------|
| `audit.jsonl` | one JSON object per line, sha256-chainable | every action, every gate decision |
| `token_log.jsonl` | one JSON object per `gateway_chat` | token spend, cache hits, model |
| `routing_decisions.jsonl` | one JSON object per DECOMPOSE | rule_id, lane, health, fallback |
| `receipts/<mission_id>-<stage>.json` | full receipt | stage evidence |
| `fused.json` | one per mission | FUSE result with chain hash |
| `delivery.json` | one per mission | final delivery with status |
| `failure.json` | one per failure | taxonomy code, owner, evidence |
| `memory.jsonl` | one per memory write | memory_write_id, key, value, tags |

All files live under `runs/<mission_id>/` and are append-only within a mission.

## Metrics (computed, not stored)

| Metric | Formula | Target |
|--------|---------|--------|
| cache_hit_ratio | cache_hits / total_reads | >= 0.30 |
| spend_ratio | spent_tokens / budget_tokens | <= 1.0 |
| lane_diversity | distinct_lanes_used / total_lanes | >= 0.40 (avoid single-lane runs) |
| three_sig_compliance | code_with_three_sigs / code_total | = 1.0 |
| fusion_dedup_rate | dedup_count / total_input_count | recorded (no target) |
| failure_rate | failures / missions | <= 0.20 |
| mean_receipt_chain_len | mean of receipt_chain length | recorded |
| reasoning_token_tax | reasoning_tokens / total_output_tokens | recorded |

## Traces

Each mission produces a trace:

```
runs/<mission_id>/trace.json
{
  "mission_id": "...",
  "stages": [
    {"stage": "INTAKE",  "ts": ..., "duration_ms": ..., "lane": "operator"},
    {"stage": "DECOMPOSE", "ts": ..., "duration_ms": ..., "lane": "operator"},
    {"stage": "DISPATCH",  "subtasks": [{"ts": ..., "lane": "REASON", "duration_ms": ...}, ...]},
    {"stage": "VERIFY",    "subtasks": [{"ts": ..., "lane": "VERIFY", "duration_ms": ...}, ...]},
    {"stage": "FUSE",      "ts": ..., "duration_ms": ..., "lane": "operator"},
    {"stage": "DELIVER",   "ts": ..., "duration_ms": ..., "lane": "operator"}
  ]
}
```

## Inspection Surface

A simple CLI reads `runs/<mission_id>/` and renders a one-screen summary:

```bash
apex-mesh status <mission_id>
# prints stage progression, spend, signatures, status, memory_write_id
```

## Gates

- **G1 — Append-only gate.** Logs are never rewritten; corrections create new entries with `supersedes`.
- **G2 — Schema gate.** Every log line is a JSON object with `ts` and `mission_id`.
- **G3 — Replay gate.** Given `audit.jsonl` + `token_log.jsonl` + `routing_decisions.jsonl` + `receipts/`, an independent verifier must be able to reconstruct the mission state. Test: replay a 24h-old mission, get the same `receipt_chain_sha256`.
- **G4 — Inspection gate.** `apex-mesh status <mission_id>` returns within 1 second for missions up to 30 days old.

## Anti-Patterns

- `print()` instead of structured logging.
- Logging to stdout only (no on-disk record).
- Logging without `mission_id` (orphaned lines).
- Metrics that require running code to recompute (must be on disk).
- Silent state in memory (closures, class attrs not persisted).

## L2 Evidence

- Every log line is a JSON object.
- Replay test passes.
- `apex-mesh status` test passes (latency, completeness).

## Versioning

- Major bump: change to log schema, change to replay contract.
- Minor bump: new metric, new log surface.

Current version: **1.0.0**
