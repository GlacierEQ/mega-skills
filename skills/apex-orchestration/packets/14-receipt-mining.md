# Packet 14 — RECEIPT-MINING

**Owner:** apex-orchestration v1.1.0
**Maturity:** 9 / "Every receipt is a labeled training example; we mine them online"
**Layer:** Skill
**Scope:** Define the offline + online pipeline that turns staged receipts into lane-quality signals, anti-pattern library updates, and prompt-template refinements.

---

## Invariant (L5)

Every delivered mission's receipts are mined at DELIVERY time (online). The miner produces (a) updated `lane_stats.json`, (b) an updated anti-pattern library entry, and (c) optional prompt-template patches. Mining is deterministic, version-chained, and replayable.

## Mining Pipeline (4 stages)

```
runs/<mission_id>/receipts/  -->  PARSE  -->  FEATURIZE  -->  AGGREGATE  -->  EMIT
       (raw)                  (validate)   (per-subtask)   (per-lane)     (lane_stats + anti-patterns)
```

1. **PARSE** — every `*.json` validated against the receipt schema (Packet 03). Invalid = drop with `parse_failure: true` audit log.
2. **FEATURIZE** — for each receipt, compute:
   - `lane`, `model`, `domain` (extracted from `task` text or path)
   - `outcome`: `success` if `l2_proof == true`, `fail` otherwise
   - `latency_ms`: from `duration_ms`
   - `tokens_in/out`: from usage if present
   - `signal_density`: 1.0 if `sha256[]` covers all `files_changed[]`, else 0.0
3. **AGGREGATE** — rolling window per lane: `success_rate`, `p50_latency`, `p95_latency`, `signal_density_mean`, `n_observations`. Window = last 50 missions per lane.
4. **EMIT** — write updated `lane_stats.json` (Packet 13) + anti-pattern library append.

## Anti-Pattern Library

Each F-XXX code from Packet 09 has an evolving entry. The miner appends a new evidence line per occurrence:

```json
{
  "code": "F-VER-01",
  "first_seen": "2026-09-04T16:00:00Z",
  "occurrences": 7,
  "last_occurrence": "2026-09-04T18:00:00Z",
  "remediation_hints": [
    "verify receipt has l2_proof before FUSE",
    "re-dispatch with stricter max_tokens"
  ],
  "lane_distribution": {"REASON": 0, "CODE": 5, "VERIFY": 0, "ROUTER-FREE": 2}
}
```

Location: `~/.local/share/apex-orchestration/anti_patterns.json`. The file is append-only; corrections create new versions with `supersedes`.

## Prompt-Template Refinement (Optional)

When a lane's `success_rate` drops below 0.5 for ≥ 5 consecutive missions, the miner emits a **suggested prompt patch**:

```json
{
  "lane": "REVIEW",
  "trigger": "consecutive_failures >= 5",
  "suggested_diff": "<unified-diff text>",
  "test_coverage": "0.0",
  "human_required": true
}
```

The patch lands in `~/.local/share/apex-orchestration/suggested_patches/<lane>-<ts>.json` and is **never auto-applied** (human in the loop per AGENTS.md §0).

## Gates

- **G1 — Determinism gate.** Running the miner twice on the same `runs/<mission_id>/` produces identical `lane_stats.json` and `anti_patterns.json` (sha256 of the outputs must match).
- **G2 — Backpressure gate.** If receipts count > 10,000, the miner streams; if any single receipt > 1 MB, it is dropped with an audit log.
- **G3 — Replay gate.** Given the receipts and a frozen `lane_stats.json` from a prior moment, re-mining produces the same updated `lane_stats.json` (verified by sha256 of pre/post).
- **G4 — Privacy gate.** Receipts may contain prompts/responses; the miner never persists prompt text. Only structured features (lane, latency, success).
- **G5 — Anti-pattern dedup gate.** A new occurrence of an existing code within the same mission is collapsed; one entry per mission per code.

## Anti-Patterns

- Mining the **prompt text** from receipts (privacy / leak risk).
- Auto-applying prompt patches (must be human-approved).
- Recomputing the entire history on every mission (O(n) is too slow; use the rolling 50-mission window).
- Allowing `lane_stats.json` to grow unbounded (cap at ~100KB; older observations compressed).

## L2 Evidence

- Determinism test: 10 receipts, 2 miner runs, byte-identical output.
- Replay test: freeze `lane_stats` at T0, run 5 missions, re-mine, sha256 of replay matches live result.
- Privacy test: feed receipts with prompt text, assert no prompt text appears in miner output.
- Anti-pattern test: feed 5 F-VER-01 receipts, assert 1 entry (collapsed), `occurrences=5`, `lane_distribution` correct.

## Versioning

- **Major bump:** mining pipeline stage change, new feature added, anti-pattern schema change.
- **Minor bump:** window size change (e.g. 50 → 100), dedup rule change.
- **Patch:** bug fix with no schema change.

Current version: **1.0.0** (paired with apex-orchestration v1.1.0).
