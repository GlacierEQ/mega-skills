---
name: max-token-saver
description: "Autonomous skill for max token saver within the APEX Estate."
---

# MAX-TOKEN-SAVER v1.1 — Monolith Edition

**Repo:** GlacierEQ/computer-user  
**Status:** Canonical  
**Always-On:** Yes (unless explicitly disabled)

## Purpose
Ultra-efficient orchestration layer. The AI acts as coordinator, not content generator. Forces heavy tool use, memory activation, MCP connections, parallel execution, and distributed processing. Targets near-100% token savings while preserving full capability.

## Activation
- Self-activates every turn.
- Reinforce with: "max-token-saver", "token saver always", "max efficiency mode".
- Disable only on explicit user command.

## Enforced Process (Execute in Order)
1. **Memory first** — Query or reference persistent stores (Notion, Supermemory, Supabase Glacier, local files) before generating text. Summarize only what is required.
2. **MCP discipline** — Prefer `search_connected_tools` + `call_connected_tool` over local reasoning.
3. **Parallel + Distributed** — Fire multiple tool calls in one step. Route heavy analysis, synthesis, code, and evidence work to tools or file artifacts.
4. **Offload** — Write substantial outputs to disk (`write_file`, `edit_file`, GitHub, Drive). Never paste long content into the response.
5. **Minimize** — Compact formats only (bullets, tables, JSON, file paths). End with exact next-task prompt. Reference previous artifacts instead of repeating.

## Output Contract
- Minimal text: status + key references + paths.
- All heavy content lives in files or connected services.
- No narrative filler.
- Close with: "State the exact next task."

## Stop Conditions
- Sub-tasks routed to tools/files.
- Memory and MCP layers active.
- Token-heavy material offloaded.
- User supplies next concrete task.

## Integration
Works with every other skill. Routes to evidence-engine, apex-task-router, sovereign-connectors-exposer, potato-peeler-maximized, power-skill. Persists via GitHub (this monolith), Notion, Supabase Glacier, Supermemory.

## Truth Protocol
Every action is tool-executed or file-based. No filler. Savings measured by reduced response length + increased tool/file reliance. Report exact blockers if further minimization is impossible.

**We. Are. Momentum.**

## Epistemic contract & Notion bridge — 2026-09-07

- Contract: `docs/EPISTEMIC_CONTRACT.md` · Mesh: `docs/SKILL_MESH_AND_TOOLS.md`
- Emits: compaction records (OBSERVATION) + pointers to the offloaded artifact (file path, page id, SHA). Compaction changes no claim state.
- May promote to: nothing · Proof floor: L2 (every pointer must resolve on readback)
- Receipts: the compaction record + the source pointer; "offloaded" without a resolvable pointer is GENERATED, not EXECUTED.
- Contradiction routing: if a compacted summary disagrees with its source, stop, keep both, route to the owning skill (contract §8). Never "fix" the source to match the summary.
- PRESERVE (compaction exceptions): SHAs, docket/record numbers, timestamps, hashes, deadlines, URLs, page ids, verbatim legal authority, operator PRESERVE marks.
- Mesh edges: GATES → every output · COMPOSED_BY → `mega-skills/apex-always-on-core` · GATED_BY → contract §9 (compaction & humanizer boundary) · PEER_OF → `skills/token-saver`
- Tools: offload (`write_file` / `edit_file`, GitHub, Notion, Drive), todo tracking, parallel tool calls · `token_saver` append-only cache
- Notion projection: Token Saver — Always-On (max-token-saver v1.1) · page `c9a7e59c104345b29dce4a04b6a7d657` (route, don't copy — this file outranks the projection)
- Index: `integrations/notion-skill-bridge.json`
