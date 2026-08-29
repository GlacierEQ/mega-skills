---
name: mega-genesis-prime
description: Genesis Prime
domains: [genesis-prime]
token_profile: Lean
---

# MEGA-GENESIS-PRIME

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Genesis Prime

Memory integration and document processing at /root/genesis-prime. Owns
the AI pipeline that ingests external sources (court filings, evidence
files, documents) and routes them into the bucket system.

**See:**
- `@/root/.agents/skills/quantum-nexus/SKILL.md` — the bucket system
- `@/root/.agents/skills/legal-powerhouse/SKILL.md` — the legal use case
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Test command:** `cd /root/genesis-prime && python -m pytest tests/ -v` (verify per repo)
- **Entry point:** `python -m genesis_prime` (verify per repo).
- **The pipeline is policy-bound.** A document must clear format + size
  + content checks before it's promoted to a bucket.
- **All ingestion writes go to the audit log** — bypass it and you lose traceability.

## Sharp edges

- Genesis Prime doesn't decide what to *do* with documents; it decides
  where to *put* them. The downstream system (legal, technical, etc.)
  decides what the documents mean.
- Source paths are user-input. Validate them; don't trust them.
  Per `security-review`, the path is untrusted input.
- If the pipeline fails, the document is in the staging area with an
  audit log entry pointing to the failure. Don't silently drop it.
