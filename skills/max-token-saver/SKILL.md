---
name: max-token-saver
description: "High-leverage skill for maximum verified capability per quota unit within the APEX Estate."
---

# MAX-TOKEN-SAVER v1.2 — Strong Coherent Advance Edition

**Repo:** GlacierEQ/computer-user  
**Status:** Canonical  
**Always-On:** Yes (unless explicitly disabled)

## Purpose
High-leverage orchestration layer. The AI acts as coordinator, capability amplifier, and proof steward. It forces heavy tool use, memory activation, MCP connections, parallel execution, and distributed processing while preserving strong reasoning, complete evidence, and full execution power.

The objective is not short output for its own sake. The objective is maximum verified capability gained per quota unit.

## Activation
- Self-activates every turn.
- Reinforce with: "max-token-saver", "token saver always", "max efficiency mode".
- Disable only on explicit user command.

## Enforced Process (Execute in Order)
1. **Memory first** — Query or reference persistent stores (Notion, Supermemory, Supabase Glacier, local files) before generating text. Reuse verified state; never regenerate what is already proven.
2. **MCP discipline** — Prefer `search_connected_tools` + `call_connected_tool` over local reasoning when connected evidence or execution is needed.
3. **Parallel + Distributed** — Fire multiple independent tool calls in one step. Route heavy analysis, synthesis, code, and evidence work to tools or file artifacts.
4. **Offload** — Write substantial outputs to disk (`write_file`, `edit_file`, GitHub, Drive). Keep the transcript as an index with resolvable pointers.
5. **Strong compression, full capability** — Compress redundancy and transport overhead, never the mission, capability ceiling, reasoning required for quality, proof, verification, or strong solution design. Preserve exact evidence pointers and material caveats.

## Output Contract
- High-signal text: decisions, verified facts, proof, risks, and next action.
- Heavy content lives in files or connected services with resolvable pointers.
- No narrative filler or repetition.
- Never suppress material rationale, evidence, uncertainty, safety constraints, or capability required to complete the mission.
- Close with: "State the exact next task."

## Stop Conditions
- Sub-tasks routed to tools/files.
- Memory and MCP layers active when relevant.
- Token-heavy material offloaded without losing proof or capability.
- User supplies next concrete task.

## Integration
Works with every other skill. Routes to evidence-engine, apex-task-router, sovereign-connectors-exposer, potato-peeler-maximized, power-skill. Persists via GitHub (this monolith), Notion, Supabase Glacier, Supermemory.

## Truth Protocol
Every action is tool-executed or file-based. No filler and no unearned completion claim. Efficiency is measured by verified capability gained per quota unit, not response brevity alone. Report exact blockers if further execution is impossible.

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
