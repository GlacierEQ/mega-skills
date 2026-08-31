---
name: mega-mermicorn-grove
description: "Mermicorn Grove"
---



# MEGA-MERMICORN-GROVE

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Mermicorn Grove

The Mermicorn Grove is a constellation registry: 15 repos spanning deals,
design, games, collectibles, commerce, and AI. The Grove is the catalog;
individual Mermicorn repos are leaves under it.

**See:**
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Grove is the catalog, not a runtime.** The Grove holds pointers to Mermicorn
  repos and their state. It does not implement features itself.
- **Each Mermicorn repo has its own skill if it needs one.** The Grove
  points at the right one.
- **Test command:** `cd /root/mermicorn-grove && python -m pytest tests/ -v` (verify per repo)
- **Entry point:** the Grove's own CLI; check its README for specifics.

## Sharp edges

- A "Mermicorn project" is any leaf registered in the Grove. The Grove
  itself is the catalog.
- Don't add business logic to the Grove. It catalogs, doesn't execute.
- New constellation entry = new leaf registered, not a refactor of the Grove.
