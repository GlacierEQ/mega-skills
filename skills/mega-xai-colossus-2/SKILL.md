---
name: mega-xai-colossus-2
description: xAI Colossus 2
domains: [xai-colossus-2]
token_profile: Lean
---

# MEGA-XAI-COLOSSUS-2

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# xAI Colossus 2

The end-to-end xAI Colossus 2 infrastructure project. The flagship of
the Colossus family (which also has cooling, energy, security, servers
variants — each is a separate repo and skill).

**See:**
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/mastermind/SKILL.md` — mastermind sidecar pattern
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow
- `@/root/.agents/skills/flagships/SKILL.md` — family context

## Quick rules

- **Test command:** `cd /root/.local/share/opencode/repos/github.com/GlacierEQ/xai-colossus-2 && python -m pytest tests/ -v` (verify per repo)
- **Colossus 2 is the end-to-end integration.** The other Colossus variants
  (cooling, energy, security, servers) are differentiated components.
- **AKOS is the governance layer** for the Colossus family.

## Sharp edges

- Don't conflate the Colossus variants. `xai-colossus-2` is the integration;
  `xai-colossus-cooling` is the thermal subsystem; etc. Each is a separate
  repo and they don't share code.
- The mastermind sidecar is the runtime companion — it logs every action
  to the receipt chain. Bypass it and you lose audit.
- xAI's actual Colossus is a real data center; this is a portfolio orbit
  project that uses the same name. Don't claim real-world deployment status.
