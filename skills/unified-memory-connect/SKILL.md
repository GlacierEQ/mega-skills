---
name: unified-memory-connect
description: "Multi-peer memory orchestration across Mem0, MemoryPlugin, Supermemory, Pinecone, Qdrant, and Notion with provenance-preserving routing and secret-safe configuration."
---

# Unified Memory Connect — APEX Polycentric Memory Mesh

This skill routes distributed context across qualified memory peers without making any provider globally canonical. Live provider/source state and provenance control proposition-specific support; retrieval failure is never factual disproof.

## Memory peers

- Mem0 — semantic memory and retrieval.
- MemoryPlugin — portable cross-platform routing/index continuity.
- Supermemory — semantic/context retrieval peer.
- Pinecone / Qdrant — vector retrieval peers where configured.
- Notion — projection/workspace peer; never substitutes for source-bearing state.

## Secret boundary

Credentials MUST NOT be embedded in this skill, registries, examples, logs, receipts, generated documentation, or committed source. Runtime adapters may reference environment-variable *names* or secret-manager identifiers only. Secret values remain in the configured vault/runtime secret store and must be redacted from diagnostics.

Expected runtime secret identifiers may include provider-specific names such as `MEM0_PRO_API_KEY`, `MEM0_REG_API_KEY`, `MEMORY_GLOBAL_KEY`, `MEMORY_DIRECT_KEY`, `SUPERMEMORY_PRIMARY_KEY`, `SUPERMEMORY_SECONDARY_KEY`, `SUPERMEMORY_TERTIARY_KEY`, `PINECONE_PRIMARY_KEY`, `QDRANT_KEY`, and `NOTION_API_KEY`; these names are configuration pointers, never values.

## Retrieval contract

1. Reuse relevant known state before rediscovery.
2. Query the smallest qualified peer set that can answer the proposition.
3. Preserve provider identity, record IDs, timestamps, versions, hashes, and retrieval state where available.
4. Deduplicate semantically equivalent hits without erasing distinct provenance.
5. Treat `retrieval_pending`, `not_searched`, `searched_not_found`, and `unavailable` as retrieval states, not proof of falsity.
6. Preserve contradictions and route them for discriminating evidence rather than silently reconciling them.
7. Promote claims only when proposition-specific source evidence supports promotion.

## Cache contract

Caching is an optimization, not authority. Cache keys should bind query + filters + provider + relevant version/scope. Cached results must retain original provenance and an explicit freshness state. A stale cache must not override newer provider-native state.

## Ingestion contract

- Batch when it improves throughput, but retain per-record provenance and idempotency keys.
- Never ingest credentials or authentication material into semantic/vector memory.
- Preserve lineage between source record, normalized representation, embedding/vector record, and downstream derivative.
- Writes require provider/tool evidence; verified mutation requires readback when available.

## Runtime discovery

Local scripts and device-specific paths are implementation details, not universal truth. Discover currently available adapters at runtime. Missing one peer must not stop unaffected execution through other qualified peers.

## Cross-estate composition

This skill composes with:
- `casey-operator-execution-kernel` for mission/continuity semantics.
- `far-away-party` for long-horizon state and lossless handoff.
- Genius-Mastery operating-loop/composition contracts for evidence-bounded capability reuse.
- Mega Skills registries and mesh routing for capability discovery.

## Verification

A memory peer is `CONNECTED` only after a live provider/tool call succeeds. A write is `VERIFIED` only after provider-side readback where supported. Configuration presence, historical success, copied documentation, or a remembered connection does not establish current connectivity.
