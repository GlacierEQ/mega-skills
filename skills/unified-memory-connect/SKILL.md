---
name: unified-memory-connect
description: "Connect and recover Mem.ai and other memory peers (Mem0, MemoryPlugin, Supermemory, vector stores) across OMP Glacier, Claude, Codex, Gemini, and ChatGPT with exact-ID boot, provenance, permission gates, and provider-native verification. Use for cross-agent memory access, MCP setup, recovery and continuity."
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


## GlacierEQ Mem.ai cross-agent runtime

**Mem.ai is a distinct provider from Mem0.** For an Operator request to connect Mem across AI clients or improve runtime boot/recovery, consult the maintained [Mem cross-agent runbook](references/glaciereq-mem-agent-runbook.md) and machine-readable [boot profile](references/glaciereq-mem-bootstrap.json). These references extend THIS existing skill; they do not establish a competing skill, new hierarchy or independent control plane. Verify provider-current documentation at `https://docs.mem.ai/mcp/setup`.

### Cross-agent connector entry point

- Native Mem.ai hosted MCP URL: `https://mcp.mem.ai/mcp` with **each client's own OAuth authentication**. The Mem connector available inside ChatGPT does not authorize an external OMP, Claude, Codex or Gemini instance.
- Native Mem.ai REST API: `https://api.mem.ai/v2`; use a scoped server-side secret, never a prompt or git content.
- Previously recorded GlacierEQ gateway: `https://glaciereq-memory-gateway.onrender.com/mcp` is a *separate recovered endpoint* that remains unverified in this session. Probe identity/permissions/tool discovery before using it. Do not substitute it for first-party Mem or treat old gateway claims as a current readback.
- OMP Glacier: integrate with the **existing** native `.omp/skills/` loader, MCP profile and `RULES.md` controls. Discover actual installed OMP version and native MCP transport first; never assume local Mac connectivity or install a second runtime.

### Mandatory boot and execution habit

1. **INTENT:** Identify the present Operator mission and its actual authorized boundary; never select a past worker's mission solely because it was most recently updated.
2. **DISCOVER:** Use the current host's registered Mem MCP to initialize, enumerate tools, and inspect granted scope; config presence proves nothing beyond `CONFIGURED`.
3. **RECOVER:** Exact-read Mem living handoff `c3054a58-409e-5ee6-9c15-eec694b9a34a`. Systems missions additionally read auto-boot manifest `6925915b-33d6-5fc9-b499-4fbe78790413` and federation charter `63f1d7cd-9202-577a-8d0d-211c40a07606`; otherwise route to the relevant owner note. Fetch **current versions** and explicit corrections.
4. **APPLY AND EXECUTE:** Recover native source IDs/evidence and build on real existing state; apply the existing APEX/Aspen/Computer-User policy: **RECOVER → MATCH INTENT/AUTHORITY → APPLY → EXECUTE → VERIFY → PRESERVE → CONTINUE**.
5. **VERIFY:** Use provider-native readback for each side effect. A Mem summary does not verify a GitHub commit, external message, court filing, application submission or deployment; one outcome must not be counted again in another system.
6. **PRESERVE:** Update the already-owning Mem note with a **complete replacement Markdown body using the exact current `version`**, then exact-ID read back current version and content. Preserve conflicting source variants, native receipt IDs, permissions, and precise next cursor. Reconcile timeouts/ambiguous writes before retrying.

Certify **CONFIGURED → INITIALIZED → DISCOVERED → READ_VERIFIED → WRITE_VERIFIED → CROSS_SESSION_APPLIED** as separate stages. Report each stage with independent host evidence. Tests must include wrong workspace, missing OAuth, conflicting provider states, stale note version, ambiguous write, task-selection drift, irrelevant restricted data, and a cold new-session application test. Static docs and an installed skill are not behavioral or provider verification.

**When NOT to activate:** Ordinary question-answering that needs neither personal continuity nor provider access; a Mem0-only task unrelated to Mem.ai connection should follow the existing Mem0 procedures; a legal or JOB case task should load its owning domain skill rather than broadcast every Mem note into an unqualified agent.
