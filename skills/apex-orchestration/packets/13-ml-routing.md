# Packet 13 — ML-ROUTING

**Owner:** apex-orchestration v1.1.0
**Maturity:** 9 / "Routing is a learned function, not a hard-coded lookup"
**Layer:** Skill
**Scope:** Augment Packet 04's hard-coded routing heuristics with a learned scoring function that observes lane outcomes over time.

---

## Invariant (L5)

A routing decision is valid iff it is the output of `select_lane(subtask, learned_state)` where `learned_state` is a deterministic projection of `runs/<mission_id>/routing_decisions.jsonl` and the prior `lane_stats.json` history. The first-match-wins hard rules from Packet 04 still apply; the learned function only selects **within** the matching hard-rule lane set.

## The Learned Scoring Function

For a candidate lane `L` on subtask `S`, the score is:

```
score(L, S) =
      w1 * success_rate(L, domain=S.domain)         # past 50 missions
    + w2 * 1 / (1 + p95_latency_ms(L) / 1000)         # tail latency
    + w3 * current_lane_health(L)                    # 0..1 from probe
    + w4 * (1 - quota_burn_rate(L))                   # 0..1
    + w5 * semantic_similarity(S.intent_embedding,
                                canonical_lane_description[L])  # 0..1
    + w6 * recency_decay(latest_observation[L])      # 0..1, exponential
```

Default weights (deterministic, versioned):
- `w1 = 0.30` (success rate)
- `w2 = 0.20` (latency)
- `w3 = 0.20` (health)
- `w4 = 0.10` (quota)
- `w5 = 0.15` (semantic)
- `w6 = 0.05` (recency)

The total sums to `1.00`; renorming on weight change is required (see Packet 16).

## Required State

| File | Format | Purpose |
|------|--------|---------|
| `~/.local/share/apex-orchestration/lane_stats.json` | JSON: `{lane: {success, total, p50_ms, p95_ms, health, quota_burn, last_seen}}` | Per-lane rolling metrics |
| `~/.local/share/apex-orchestration/embeddings/<lane>.json` | `{vector: [384 floats], updated: ISO8601}` | Canonical lane description embeddings |
| `runs/<mission_id>/routing_decisions.jsonl` | one JSON object per decision: `{subtask_id, rule_id, lane, score, ts}` | Append-only decision log |

The state files are **derived**, not hand-edited. The orchestrator writes them; Packet 16 reads them for the learning update.

## Gates

- **G1 — Hard-rule gate.** A lane that violates a Packet 04 hard rule (R-MEDICAL → DOMAIN-MED only, etc.) gets `score = -inf` regardless of learned state. The learned function only ranks within the hard-rule-matched candidate set.
- **G2 — Score reproducibility gate.** For the same `learned_state`, the function must return identical scores. Verified by test: feed the same state twice, scores must match to floating-point exact.
- **G3 — Cold-start gate.** If `lane_stats.json` is missing or has < 5 observations for a lane, the lane's learned `success_rate` defaults to `0.5` (neutral prior). Never bias the cold start.
- **G4 — Embedding gate.** `semantic_similarity` is cosine similarity in [-1, 1]; any value outside that range is a defect (log and clamp to 0).
- **G5 — Quota-burn gate.** If `quota_burn_rate >= 1.0`, lane is excluded from candidates (BLOCK per Packet 09 F-DIS-02).
- **G6 — State integrity gate.** `lane_stats.json` is sha256-checked on every load; mismatch = abort, fall back to cold-start.

## Anti-Patterns

- Using the learned function as a black box (the score components MUST be explainable; no opaque embeddings alone).
- Letting the learned function override Packet 04 hard rules.
- Updating weights without bumping `WEIGHTS_VERSION` and recording a regression test.
- Caching the learned state in memory but writing to disk only at DELIVERY (must write incrementally).

## L2 Evidence

- `select_lane` unit tests with known inputs and expected scores.
- Reproducibility test: same state, two calls, identical score.
- Hard-rule precedence test: even with score=1.0, a hard-rule violation returns `-inf`.
- Cold-start test: empty `lane_stats.json` → neutral prior → deterministic ranking.
- Embedding integrity test: out-of-range cosine is clamped and logged.

## Versioning

- **Major bump:** weight change > 5%, score formula change, hard-rule change.
- **Minor bump:** weight change ≤ 5%, new scoring component added.
- **Patch:** bug fix in the function with no formula change.

Current version: **1.0.0** (paired with apex-orchestration v1.1.0).
