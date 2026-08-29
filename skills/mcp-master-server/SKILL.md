---
name: mcp-master-server
description: Operating inside the MCP Master Server at /root/mcp-master-server. Unified
  tool interface and server orchestration. Use when wiring new MCP servers or debugging
  the orchestrator.
version: 0.1.0
---

# MCP Master Server

The unified MCP tool interface and server orchestrator at the top of the
connector stack. Other MCP servers (mastermind, tower, genesis-prime,
legal-powerhouse, omni-engine, courtlistener) register with the master
and are exposed through a single tool surface.

**See:**
- `@/root/.agents/skills/aspen-grove-connectors/SKILL.md` — the connectors it orchestrates
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/clean-code/SKILL.md` — code style

## Quick rules

- **Test command:** `cd /root/mcp-master-server && npm test` (verify per repo; this is a Node.js project)
- **The master is a router, not a worker.** It delegates; it doesn't implement
  the underlying tools itself.
- **Adding a new MCP server:** register it in `opencode.jsonc` under `mcp:`
  AND in the master's own server list, then run `python3 /root/sync_kilocode_mcp.py`
  to keep Kilo's config in sync.
- **Health checks:** the master exposes a `/health` endpoint; check it first
  when a downstream consumer is failing.

## Sharp edges

- The master is a single point of failure for the tool surface. Run it
  in a way that restarts on crash.
- Server discovery uses the path/PYTHONPATH from `opencode.jsonc`. If a
  server fails to register, check the env vars in the config first.
- Don't add business logic to the master. Delegate, don't absorb.
