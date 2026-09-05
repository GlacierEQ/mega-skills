# Packet 25 — RETRIEVAL-AUGMENTED-CONTEXT

**Owner:** apex-orchestration v1.3.0
**Maturity:** 9 / "Past missions inform future ones; the mesh learns from itself"
**Layer:** Skill
**Scope:** At INTAKE, recall the top-k similar past missions from the embedding memory (Packet 15) and inject their summaries as context for the current mission. This grounds the orchestrator in prior experience without re-deriving decisions.

---

## Invariant (L5)

A retrieval-augmented context (RAC) is valid iff:
1. The top-k recalls have `cosine similarity >= RAG_THRESHOLD` (default 0.80).
2. The top-k are returned in descending similarity order (stable tiebreak by mission_id).
3. Each recall's summary is included verbatim (no paraphrasing).
4. The RAC is logged: `runs/<mission_id>/rag_context.jsonl` with `{ts, query, recalls: [{mission_id, similarity, summary_ref}]}`.
5. If `len(recalls) == 0`, the RAC is empty — the mission proceeds with no context (no error).

## The RAG Algorithm

```
recall_similar(mission_intent, k=5, threshold=0.80) -> list[Recall]:
    q = embed_intent(mission_intent)
    candidates = read_index(domain_tag=None)  # all domains
    scored = [(c, cosine(q, read_vector(c.mission_id))) for c in candidates]
    filtered = [(c, s) for c, s in scored if s >= threshold]
    return sorted(filtered, key=lambda x: (-x[1], x[0].mission_id))[:k]
```

## Context Injection

For each recall, the summary is formatted as:

```
[RECALL mission_id=<id> similarity=<score>]
<summary content>
[/RECALL]
```

The RAC is prepended to the orchestrator's system context. The DISPATCH phase may also use RAC to inform per-subtask routing.

## Gates

- **G1 — Threshold gate.** RAG_THRESHOLD = 0.80 (configurable). Lower → noise; higher → only near-duplicates.
- **G2 — Top-k cap gate.** Default `k = 5`. Higher → token bloat. Lower → may miss relevant context.
- **G3 — Stable-order gate.** Same input → same recall order (verified by test).
- **G4 — Empty-result gate.** No recalls is not an error. The mission proceeds normally.
- **G5 — Privacy gate.** Recall summaries may contain user-specific data. The RAC is never persisted outside `runs/<mission_id>/` (per Packet 10 boundary).

## Anti-Patterns

- Using RAC for deterministic tasks (overhead, no value).
- Re-ranking recalls based on recency only (loses similarity signal).
- Persisting the RAC outside the mission's run directory (privacy violation).
- Treating RAC as authoritative (it's a hint, not a mandate).

## L2 Evidence

- Threshold test: cosine = 0.79 → excluded. 0.80 → included.
- Order test: top-k returned in descending similarity.
- Empty test: zero matches → empty RAC, no error.
- Privacy test: RAC file is in `runs/<mission_id>/` only.

## Versioning

- **Major bump:** threshold default change.
- **Minor bump:** new recall format.
- **Patch:** bug fix.

Current version: **1.0.0** (paired with apex-orchestration v1.3.0).
