---
name: mega-legacy-estate
description: "Legacy Estate (GlacierEQ)"
---



# MEGA-LEGACY-ESTATE

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Legacy Estate (GlacierEQ)

The 403 older source repos under the GlacierEQ account — pushed before
the August 2026 burst, not a flagship, not portfolio, not a fork.
**Stale or completed work**, kept on the account for the public record.

## Estate shape (audit 2026-08-28)

- **~403 source repos** in this family
- Push date distribution: 333 from May 2026, 38 from June 2026, 30 from July 2026,
  1 from March 2026, 1 from July 2025
- Mostly Python + TypeScript + JavaScript
- Some are experimental prototypes that were never promoted to flagships
- Some are completed engagements (the orbit they were targeting has moved on)

## Pattern recognition

Legacy-estate repos typically have:

- **Older push date** (before 2026-08-20)
- **Name often experimental** (e.g. `RHLQ`, `BLAH-blah`, `Prototype-X`,
  `Aegis`, `Gorgon`, `Mneme`, `PhoenixOps`, `Polaris`, `Tartarus`)
- **May or may not have tests**
- **May have an AGENTS.md** but it's often an earlier-generation template

## How legacy-estate differs from active work

| Aspect | Legacy | Active (flagships, innovations) |
|---|---|---|
| Push recency | Older | Recent |
| Maintenance | Stopped or slow | Active |
| Conventional role | Reference / archive | Working |
| Upgrade target | None | Continuous |

## Working in a legacy-estate repo

1. **First, ask: does this still need to be a repo?** Many legacy repos are
   no longer maintained. The right move might be to archive, not edit.
2. **If the user wants to revive it**, treat it as a new project — load
   `clean-code` and `codemaster` and follow the standard recipe.
3. **If the user wants to read it as reference**, do that. Don't make changes.
4. **If the user wants to use it as a base for a new project**, fork it
   out (or copy locally) and start a new source repo. Don't promote the
   legacy repo itself.

## Hard Rules

1. **Don't promote a legacy repo to flagship status without explicit user direction.**
   Flagship status implies active maintenance.
2. **Don't "fix" a legacy repo's tests** unless the user asks. Many legacy
   repos have known-broken tests that were intentionally left as-is.
3. **The "Identity" prose in some legacy repos is from an earlier template
   generation.** Treat as historical artifact, not current doctrine.
4. **If the legacy repo has an AGENTS.md skill pointer**, follow it. Otherwise
   this skill is the contract.

## When this skill does NOT apply

- **Active flagships (22)**: see `flagships`
- **Engineering innovations (195)**: see `engineering-innovations`
- **Portfolio (48)**: see `job-app-portfolio`
- **Forks (513)**: see `forks`

## Related Skills

- `flagships` — for the 22 source projects
- `engineering-innovations` — for the 195 recent source projects
- `job-app-portfolio` — for the 48 orbit-targeted repos
- `forks` — for the 513 private inbound forks
- `apex-sovereign-runtime` — for APEX-family doctrine
- `pro-code` — Pro Code methodology (where applicable)
- `clean-code` — code style
- `codemaster` — coding workflow
