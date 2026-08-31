---
name: aspen-grove-connectors
description: "Operating inside the Aspen Grove MCP connector family at /root/projects/aspen-grove-connectors. Bridges to GitHub, Notion, Supabase, Dropbox, ClickUp, Linear, Vercel, DuckDB, Taskade, MemoryPlugin, Pinecone. Use when wiring a new external service or debugging a connector."
---



# Aspen Grove Connectors

The MCP connector mesh for the GlacierEQ estate. One connector per external
service: GitHub, Notion, Supabase, Dropbox, ClickUp, Linear, Vercel, DuckDB,
Taskade, MemoryPlugin, Pinecone. Plus specialized connectors (Smithery,
E2B code interpreter).

**See:**
- `@/root/.agents/skills/mastermind/SKILL.md` — runtime that consumes the connectors
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/apex-integrations/SKILL.md` — service-connector pattern
- `@/root/.agents/skills/clean-code/SKILL.md` — code style

## Quick rules

- **Test command:** `cd /root/projects/aspen-grove-connectors && python -m pytest tests/ -v`
- **Entry point:** each connector has its own CLI/MCP entry; check the connector's README.
- **All credentials go in `/root/.secrets/<name>`, not in source.**
  The `opencode.jsonc` pattern uses `{file:/root/.secrets/<name>}` references.
- **Run `python3 /root/sync_kilocode_mcp.py` after editing `opencode.jsonc`** so
  the Kilo MCP config stays in sync.

## Sharp edges

- Each connector must have a working test that hits a sandbox or mock endpoint.
  Real-credential tests belong in integration suites, not unit tests.
- Don't change a connector's public surface without checking which
  consumers in mastermind / helix / monolith depend on it.
- When a connector's external API changes, the receipt log on the connector
  is the first place to look.
