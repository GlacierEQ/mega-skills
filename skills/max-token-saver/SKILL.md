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
