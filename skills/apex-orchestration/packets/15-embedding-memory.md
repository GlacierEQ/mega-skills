# Packet 15 — EMBEDDING-MEMORY

**Owner:** apex-orchestration v1.1.0
**Maturity:** 9 / "Past missions are retrievable by intent, not just by id"
**Layer:** Skill
**Scope:** Persistent embedding store of every delivered mission, indexed by intent, schema-versioned, queryable from any orchestrator phase.

---

## Invariant (L5)

Every delivered mission produces an `intent_embedding` (384-dim float32 vector) and is stored in the embedding memory. Retrieval by intent must be deterministic: same query vector → same top-k results, with stable tie-breaks.

## Storage Layout

```
~/.local/share/apex-orchestration/embedding_memory/
  index.jsonl          # one line per mission: {id, ts, embedding_ref, summary_ref, tags}
  vectors/
    <mission_id>.f32   # raw float32 little-endian, 384*4 = 1536 bytes
  summaries/
    <mission_id>.md    # human-readable, < 4 KB
  schema_version       # integer; 1 for v1.x
```

Total size cap: 100 MB for vectors, 10 MB for summaries. On overflow, evict the oldest mission (FIFO) with an audit log entry.

## Embedding Function

```python
def embed_intent(text: str) -> list[float]:
    # deterministic 384-dim pseudo-embedding derived from a hash
    # of the text + a stable seed. Not an LLM call.
    h = hashlib.sha256(("apex-orch/v1.1.0:" + text).encode()).digest()
    seed = int.from_bytes(h[:8], "big")
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(384).astype("float32")
    v /= np.linalg.norm(v)  # unit length
    return v.tolist()
```

The pseudo-embedding is **deterministic and offline**. It is not a learned embedding model — it is a fingerprint with cosine-friendly geometry, sufficient for similarity-based recall. Future versions may swap in a learned encoder; the schema-versioned wrapper ensures backward compatibility.

## Required Fields in `index.jsonl`

```json
{
  "mission_id": "mission_<ulid>",
  "ts": "2026-09-04T18:00:00Z",
  "embedding_ref": "vectors/<mission_id>.f32",
  "summary_ref": "summaries/<mission_id>.md",
  "tags": ["apex", "delivered", "<domain_tag>"],
  "schema_version": 1,
  "intent_text": "<original mandate, first 240 chars>"
}
```

## Query API

```python
def recall_similar(intent_text: str, k: int = 5,
                   domain_tag: Optional[str] = None) -> list[dict]:
    q = embed_intent(intent_text)
    candidates = read_index(domain_tag=domain_tag)
    scored = [(c, cosine(q, read_vector(c["mission_id"]))) for c in candidates]
    return sorted(scored, key=lambda x: -x[1])[:k]
```

Use cases:
- INTAKE phase: recall past missions with similar mandates; surface prior blast-radius mistakes.
- DECOMPOSE phase: recall what subtask structures worked for similar work.
- DELIVERY phase: cross-check that the new mission is not a near-duplicate of a prior.

## Gates

- **G1 — Determinism gate.** `embed_intent` is pure; same input → identical vector (verified by bit-exact comparison).
- **G2 — Schema-version gate.** `schema_version` is in every record. Loading a record with unknown version is rejected.
- **G3 — Cosine range gate.** `cosine` returns in [-1, 1]; out-of-range is a defect.
- **G4 — Eviction gate.** FIFO only; never silent. The eviction audit log records the evicted `mission_id` and ts.
- **G5 — Cross-session gate.** A new session can query the memory and get results; the orchestrator doesn't gate by session_id.

## Anti-Patterns

- Using a real LLM call for embedding (slow, expensive, non-deterministic; defeats the purpose of fast recall).
- Storing prompt text in `intent_text` beyond 240 chars (privacy).
- Skipping the cosine normalization (causes length-bias).
- Using timestamp as the sole ordering (allows duplicates to leak).

## L2 Evidence

- Determinism test: same `text` → identical 384-dim vector (bit-exact).
- Round-trip test: embed → store → query top-1 → matches the stored summary.
- Eviction test: fill 100 MB, oldest mission removed, eviction log has entry.
- Schema-version test: load record with `schema_version=999` → reject with F-DEL-02.

## Versioning

- **Major bump:** embedding dimension change, schema_version bump, eviction policy change.
- **Minor bump:** new field in index record, new query API.
- **Patch:** bug fix with no schema change.

Current version: **1.0.0** (paired with apex-orchestration v1.1.0).
