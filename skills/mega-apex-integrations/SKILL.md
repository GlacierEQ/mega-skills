---
name: mega-apex-integrations
description: "Apex Integrations"
---



# MEGA-APEX-INTEGRATIONS

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Apex Integrations

Service-connector layer for the APEX family. Bridges between legal (courtlistener,
casey-legal), memory (quantum_nexus, mermicorn), and runtime (mastermind, tower)
systems. New connectors go here, not into the consuming project.

**See:**
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/mastermind/SKILL.md` — runtime target
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Test command:** `cd /root/projects/apex-integrations && python -m pytest tests/ -v`
- **Entry point:** `python -m apex_integrations` (verify per repo)
- **Connectors are policy-bound.** Each connector carries identity + scope.
- **No secrets in source.** Reference them via `/root/.secrets/<name>` like the
  `opencode.jsonc` pattern (use `{file:...}` placeholders, not inline values).

## Sharp edges

- Don't import downstream runtime modules from this repo. Connectors are
  callable from downstream, not the other way around.
- New connector = new test file. No exceptions.
- When a connector fails, the failure is logged, not raised. Let callers
  decide how to handle.
