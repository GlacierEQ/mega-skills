---
name: mega-flagships
description: Flagships (GlacierEQ)
domains: [flagships]
token_profile: Lean
---

# MEGA-FLAGSHIPS

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Flagships (GlacierEQ)

The 22 first-class projects under the GlacierEQ account. Each is a substantial,
ongoing engineering effort with its own runtime, doctrine, and skill.

**Do not treat flagships as one homogeneous group.** Each has its own skill,
its own test command, and its own conventions. Use this skill to route to
the right one.

## Flagship roster (22)

### Tier 1: APEX core (have dedicated skills)

| Project | Skill | Test command | Notes |
|---------|-------|--------------|-------|
| `monolith` | `monolith` | `cd /root/projects/monolith && python -m pytest tests/ -v` | Meta-layer: catalog + propagation |
| `mastermind` | `mastermind` | `cd /root/projects/mastermind && python -m pytest tests/ -v` | Mission-control runtime |
| `make-it-heavy` | `make-it-heavy` | `cd /root/projects/make-it-heavy && python -m unittest discover tests` | Multi-agent swarm |
| `the-tower-of-babel` | `tower-of-babel` | `cd /root/projects/GlacierEQ_Swarm/the-tower-of-babel && pytest` | Technology authority |
| `apex-control-plane` | (use `apex-sovereign-runtime` + `flagships`) | n/a yet | Source identity |
| `apex-singularity-head` | (use `apex-sovereign-runtime` + `flagships`) | n/a yet | Master architecture |
| `apex-cli` | (use `apex-sovereign-runtime` + `flagships`) | n/a yet | CLI surface |

### Tier 2: APEX family / integrations

| Project | Skill | Notes |
|---------|-------|-------|
| `GlacierEQ_Swarm` | (use `apex-sovereign-runtime` + `flagships`) | Monorepo |
| `apex-integrations` | (use `apex-sovereign-runtime` + `flagships`) | Integrations |
| `aspen-grove-connectors` | (use `apex-sovereign-runtime` + `flagships`) | Connectors |
| `ai-deal-finder` | (use `apex-sovereign-runtime` + `flagships`) | |
| `colossus-gateway` | (use `apex-sovereign-runtime` + `flagships`) | |
| `colossus-training-flux` | (use `apex-sovereign-runtime` + `flagships`) | |
| `genesis-prime` | (use `apex-sovereign-runtime` + `flagships`) | |
| `mcp-master-server` | (use `apex-sovereign-runtime` + `flagships`) | |
| `omni_engine` | (use `apex-sovereign-runtime` + `flagships`) | |
| `mermicorn` | (use `apex-sovereign-runtime` + `flagships`) | |
| `Pro-comet-agent` | (use `apex-sovereign-runtime` + `flagships`) | |
| `ECHO` | (use `apex-sovereign-runtime` + `flagships`) | |
| `antigravity-cli` | (use `apex-sovereign-runtime` + `flagships`) | |
| `public-actions-runner-host` | (use `apex-sovereign-runtime` + `flagships`) | |
| `job-app-helix` | (no dedicated skill — use `flagships` + `job-app-portfolio`) | Portfolio orchestrator |
| `glaciereq-mcp-stack` | (use `apex-sovereign-runtime` + `flagships`) | |

## Picking the right skill

1. **If the project has a dedicated skill** (Tier 1: `monolith`, `mastermind`,
   `make-it-heavy`, `tower-of-babel`), load that skill.
2. **If the project is APEX-family but doesn't have a dedicated skill** (Tier 2),
   load both `apex-sovereign-runtime` and `flagships`.
3. **If the project is `job-app-helix`** (the portfolio orchestrator), load
   `job-app-portfolio` for the family contract and `flagships` for routing.
4. **If unsure**, load `flagships` first, then follow the references.

## Hard Rules

1. **Each flagship has its own conventions.** Do not assume make-it-heavy style
   applies to mastermind, or vice versa.
2. **The APEX doctrine is shared** across the family: receipt chains, identity
   gating, lane routing. See `apex-sovereign-runtime`.
3. **Some flagships have active doctrine in their AGENTS.md** (mastermind, monolith,
   tower). Read it before editing.
4. **The flagships are real projects, not templates.** The "Identity" prose in
   some is real methodology (Pro Code philosophy, Apex doctrine). Treat it as
   operational discipline, not identity-installation.

## Related Skills

- `apex-sovereign-runtime` — the shared APEX doctrine
- `monolith`, `mastermind`, `make-it-heavy`, `tower-of-babel` — Tier 1 dedicated skills
- `engineering-innovations` — the 195 recent non-flagship repos
- `job-app-portfolio` — the 48 orbit-targeted repos
- `forks` — the 513 private inbound forks
- `pro-code` — Pro Code methodology
- `clean-code` — code style
- `codemaster` — coding workflow
