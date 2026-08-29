---
name: ai-deal-finder
description: Operating inside AI Deal Finder at /root/projects/ai-deal-finder. Use
  when working on the deal-discovery and matching pipeline.
version: 0.1.0
---

# AI Deal Finder

Deal-discovery and matching pipeline at /root/projects/ai-deal-finder.
Identifies candidate deals from sources, scores them, and routes them
to the appropriate orbit (job app, Mermicorn commerce, or external).

**See:**
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Test command:** `cd /root/projects/ai-deal-finder && python -m pytest tests/ -v` (verify per repo)
- **Entry point:** check the repo's own CLI / `__main__.py`.
- **Deal scoring is policy-bound.** A deal must clear the configured thresholds
  before it's promoted.

## Sharp edges

- A "deal" here is a candidate, not a closed transaction. Don't claim
  conversion without the downstream receipt chain confirming it.
- External sources (Crunchbase, Pitchbook, etc.) require live credentials.
  Keep them in `/root/.secrets/`, not in source.
- Scoring thresholds should be in config, not hardcoded. Hardcoded
  thresholds are a re-deployment to change.
