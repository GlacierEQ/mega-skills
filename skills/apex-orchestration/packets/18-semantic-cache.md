# Packet 18 — SEMANTIC-CACHE

**Owner:** apex-orchestration v1.2.0
**Maturity:** 9 / "30-70% cost reduction on repeated intents; never serves stale results"
**Layer:** Skill
**Scope:** Before dispatching a subtask, check if a previous receipt's input intent is semantically identical (cosine >= 0.95) to the current one. If yes, return the cached output with `cache_hit: true`.

---

## Invariant (L5)

A semantic-cache hit is valid iff:
1. The cached receipt was for the same lane AND same `task_type` AND the `output` is structurally valid (sha256 still resolves).
2. The cosine similarity between the cached `intent_embedding` and the current one is >= `CACHE_THRESHOLD` (default 0.95).
3. The cached receipt is no older than `CACHE_TTL_HOURS` (default 168 = 1 week).
4. The cache hit is recorded in `runs/<mission_id>/cache_log.jsonl` and in `lane_stats.json.cached_draft_count`.

## Cache Layout

```
~/.local/share/apex-orchestration/semantic_cache/
  index.jsonl          # one line per cache entry: {key, lane, task_type, ts, ttl_hours, ref}
  entries/
    <sha256>.json      # full receipt including output
  schema_version       # 1
```

Index keys: `sha256(f"{lane}|{task_type}|{intent_embedding_top_4_dims_quantized}")`. The quantized key is a fast prefix lookup; cosine is the final arbiter.

## The Algorithm

```
lookup(subtask):
    q = embed_intent(subtask.intent)
    candidates = read_index(lane=subtask.lane, task_type=subtask.task_type)
    for c in candidates:
        if c.ttl_expired(): continue
        cached_vec = read_entry(c.ref).intent_embedding
        sim = cosine(q, cached_vec)
        if sim >= 0.95:
            return CacheHit(receipt=read_entry(c.ref), similarity=sim)
    return CacheMiss
```

## Cache Write (on receipt with l2_proof=true)

```
cache_write(receipt):
    key = sha256(f"{lane}|{task_type}|{quantize(intent_embedding, 4)}")
    write entries/<key>.json = {receipt, intent_embedding, ts}
    append index.jsonl: {key, lane, task_type, ts, ttl_hours: 168}
    evict entries older than CACHE_TTL_HOURS
```

## Gates

- **G1 — Threshold gate.** CACHE_THRESHOLD = 0.95 is a hard floor. Lowering it to 0.90 makes the cache too aggressive (silently serving wrong answers); raising to 0.99 makes it useless (never hits).
- **G2 — TTL gate.** Expired entries are never returned; they are evicted on access (lazy eviction).
- **G3 — Lane-scope gate.** A hit on `CODE` lane does NOT serve a `VERIFY` lane task. Cache is lane-scoped (different quality bars).
- **G4 — Schema-version gate.** Records with unknown `schema_version` are dropped, not returned.
- **G5 — Audit gate.** Every hit and miss is logged. The log is the source of truth for measuring cache effectiveness (Packet 14 anti-pattern detection).

## Anti-Patterns

- Caching side-effectful tasks (write, deploy, send) — these must always re-execute.
- Caching across users / tenants / sessions that have different permissions.
- Returning a hit when the cached `output` references files that have since changed (stale-reference anti-pattern).
- Letting the cache grow unbounded (cap at ~50 MB / 10,000 entries).

## L2 Evidence

- Threshold test: cosine = 0.94 → miss. 0.95 → hit. 0.96 → hit. Deterministic.
- TTL test: entry with `ts = now - 200h` → expired → miss.
- Lane-scope test: cached `CODE` entry does NOT match `VERIFY` query.
- Audit test: hit + miss counted correctly in `cache_log.jsonl`.
- Stale-reference test: cached output references `/tmp/x.txt` deleted between cache write and lookup → miss.

## Versioning

- **Major bump:** threshold change, schema change.
- **Minor bump:** new metadata in cache entry.
- **Patch:** bug fix in eviction.

Current version: **1.0.0** (paired with apex-orchestration v1.2.0).
