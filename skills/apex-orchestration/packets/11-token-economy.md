# Packet 11 — TOKEN-ECONOMY

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Cache-hit, surgical injection, diamond routing, hard budget"
**Layer:** Skill
**Scope:** Token spend policy for the orchestrator and its lanes.

---

## Invariant (L5)

The orchestrator and lanes spend tokens iff:

1. The spend is allocated against a `mission.budget.tokens`.
2. A `cache_hit_check` ran before the spend (see savings techniques).
3. Context injection is surgical (pointer index, not full file load).
4. Reasoning-heavy lanes have `max_tokens >= 80` (Packet 04 G4).
5. The spend is logged in `token_log.jsonl`.

## Token Budget

```
mission.budget.tokens = (
    base_per_lane * lane_count
  + context_load_cost
  + reasoning_buffer  // 1.5x for REASON, THINK-DEEP, VERIFY
  + safety_margin     // 1.2x
)
```

## Savings Techniques (apply all)

| Technique | Where | Effect |
|-----------|-------|--------|
| Pointer index before dir scan | everywhere | -85% tokens |
| Exact grep before full file read | file ops | -70% tokens |
| Cache-hit on repeated state | DISPATCH | -42.5% tokens on repeats |
| Parallel vs sequential | DISPATCH | N→1 |
| StartLine/EndLine on every read | file ops | -60 to -90% |
| Diamond 9-facet routing | context injection | -89% |
| Surgical system prompt per lane | DISPATCH | -75% vs shared prompt |

## Lane Cost Class

| Lane | Cost class | Notes |
|------|-----------|-------|
| ROUTER-FREE | free, unreliable | smoke only |
| DOMAIN-MED / DOMAIN-FIN | free, narrow | only domain questions |
| NANO-PERCEPTION | free, multimodal | only image/video/audio |
| CODE / CODE-FAST | free, code | default for code |
| VERIFY / REVIEW | free, audit | always paired with code |
| LONG-CTX / LONG-CTX-ALT | free, 1M | only long input |
| REASON | free, heavy | plans only |
| THINK-DEEP | free, heavy | long horizon only |

All lanes are on the free tier. There is no "expensive lane." Spend is bounded by `max_tokens` per call, not by model price.

## Max Tokens Defaults

| Lane | min | default | max |
|------|----:|--------:|----:|
| ROUTER-FREE | 32 | 64 | 256 |
| CODE / CODE-FAST | 256 | 1024 | 4096 |
| VERIFY / REVIEW | 256 | 1024 | 4096 |
| REASON | 512 | 2048 | 8192 |
| THINK-DEEP | 512 | 2048 | 8192 |
| LONG-CTX | 256 | 1024 | 4096 |
| DOMAIN-MED / DOMAIN-FIN | 256 | 1024 | 4096 |
| NANO-PERCEPTION | 256 | 1024 | 4096 |

`min` is the hard floor; reasoning-heavy lanes below 80 will return null/empty (verified empirically 2026-09-04, see handoff).

## Gates

- **G1 — Budget hard gate.** When `spent >= mission.budget.tokens`, no more dispatches. DELIVERY is BLOCKED with cause.
- **G2 — Cache-hit gate.** Before any expensive state read, check `optimizer_cache`. Misses are written back; hits short-circuit.
- **G3 — Surgical-injection gate.** No `read_file` of an entire file > 2000 lines without `start_line` / `end_line`.
- **G4 — Reasoning-token gate.** Reasoning lanes must have `max_tokens >= 80`. Lower = force-reject the dispatch.
- **G5 — Spend-log gate.** Every `gateway_chat` call logs `tokens_in`, `tokens_out`, `cost`, `cache_hit`, `lane`, `mission_id`.

## Anti-Patterns

- Re-reading a file that was just read.
- Re-asking a lane a question it already answered (use FUSE artifact).
- Setting `max_tokens: 10` on a reasoning model.
- Loading full conversation history into every dispatch.
- Reading `~/.local/share/kilo/kilo.db` row-by-row instead of via SQL aggregate.

## L2 Evidence

- `token_log.jsonl` with one line per `gateway_chat` call.
- Cache-hit ratio per mission (target: >= 0.30).
- Spend vs budget, reported at every stage transition.

## Versioning

- Major bump: budget calculation change, max_tokens default drop.
- Minor bump: new savings technique added.

Current version: **1.0.0**
