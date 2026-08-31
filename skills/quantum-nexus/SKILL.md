---
name: quantum-nexus
description: "Operating inside the Quantum Legal Intelligence System at /root/quantum_nexus. Vault, memory, CourtListener integration, MCP server, and the buckets (identity, legal, technical, memory, services, cloud). Use when working on legal intelligence, vault, or the memory bucket system."
---



# Quantum Nexus

The Quantum Legal Intelligence System. Provides the vault, persistent memory,
CourtListener integration, and the MCP server at `quantum_nexus.mcp.fastmcp_server`.
Also owns the **buckets** subsystem: identity, legal, technical, memory, services,
cloud — specialized memory stores with their own read/write policies.

**See:**
- `@/root/.agents/skills/legal-powerhouse/SKILL.md` — what consumes the legal bucket
- `@/root/.agents/skills/casey-legal-mcp-server` (referenced) — MCP exposure
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/security-review/SKILL.md` — vault security

## Quick rules

- **Test command:** `cd /root/quantum_nexus && python -m pytest tests/ -v` (verify per repo)
- **PYTHONPATH=/root is required** for `from quantum_nexus import ...` to work.
  The MCP server in `opencode.jsonc` sets this automatically.
- **The vault is at `/root/.vault_env`** — never copy secrets into source.
  Use `{file:/root/.secrets/<name>}` references in config.
- **Bucket reads are scoped by user_id.** Empty user_id is a hard error.
  Per `conversation-memory` skill.

## Sharp edges

- The vault contains production secrets. Treat the file as restricted.
  Don't log it; don't inline it; don't commit it.
- Bucket writes go through the audit log automatically. Don't bypass.
- CourtListener integration has its own rate limits; back off on 429s.
