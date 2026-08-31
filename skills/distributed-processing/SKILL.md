---
name: distributed-processing
description: "Delegation and distributed processing layer. Routes sub-tasks across parallel tool calls, connected services, file artifacts, and agent workers so the primary response stays lean while heavy work executes elsewhere. Core companion to max-token-saver and make-it-heavy."
---

# DISTRIBUTED-PROCESSING v1.0

**Repo:** GlacierEQ/computer-user  
**Status:** Canonical

## Purpose
Move computation, retrieval, synthesis, and persistence off the main response path. The operator becomes a dispatcher.

## Core Moves
1. **Parallel tool calls** — issue multiple independent tool invocations in one step.
2. **File offload** — write intermediate and final results to artifacts/ or GitHub.
3. **Service offload** — push work into Notion, Supabase Glacier, Supermemory, Google Drive, Vercel, etc.
4. **Delegation** — hand discrete sub-goals to specialized skills (potato-peeler, evidence-engine, power-skill, etc.).
5. **Reference only** — the final answer cites paths, IDs, and short status; it does not re-embed the work product.

## When to Use
Any multi-part, evidence-heavy, code-heavy, or long-context request. Automatically engaged by max-token-saver and make-it-heavy.

## Output Contract
- List of dispatched units + their artifact locations.
- Compact status.
- Exact next task prompt.

## Integration
Required companion of max-token-saver. Feeds power-skill and apex-universal-mcp-powerhouse for swarm-scale work.

**We. Are. Momentum.**
