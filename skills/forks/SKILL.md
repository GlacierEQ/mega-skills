---
name: forks
description: Operating inside one of the 513 GlacierEQ private inbound forks. These
  are private copies of public upstream projects, kept for reference, contribution,
  or downstream packaging. Use this skill when working in any repo under github.com/GlacierEQ/
  that has fork=true.
version: 0.1.0
---

# Forks (GlacierEQ)

The 513 private inbound forks under the GlacierEQ account. These are
private copies of public upstream projects, kept for reference, contribution
tracking, or downstream packaging.

## Estate shape (audit 2026-08-28)

- **513 forks** (all private)
- All have `fork: true` flag
- Span a wide range of upstream projects (OSS tooling, AI/ML libraries, etc.)
- Mostly Python + TypeScript + JavaScript
- No public visibility — owner-only

## How forks differ from sources

| Aspect | Source repo | Fork |
|---|---|---|
| Visibility | Public or private | All private in this estate |
| Upstream relationship | None | Tracks an upstream repo |
| Push direction | Direct edits | Sync from upstream + local commits |
| Conventional role | Product | Reference / contribution / packaging |
| Owned maintenance | Primary | Secondary |

## Working in a fork

1. **Identify the upstream.** The fork's GitHub UI shows "forked from
   `<upstream-owner>/<upstream-repo>`". The CLI shows it under
   `parent` in the API response.
2. **Check the divergence.** Run `git fetch upstream` and `git log upstream/main..HEAD`
   to see local commits not yet in upstream.
3. **If contributing back**, follow upstream's contribution guidelines.
   Their `CONTRIBUTING.md` and `AGENTS.md` (if any) take precedence.
4. **If the fork is a reference copy**, treat it as read-mostly. Local
   edits are unlikely to be the right move; read the upstream instead.
5. **If the fork is for downstream packaging**, follow the upstream's
   versioning and changelog; don't diverge silently.

## Hard Rules

1. **Don't make this fork a working repo unless that's the explicit purpose.**
   Forks drift from upstream; that's by design.
2. **Don't push to upstream unless the user asks.** The token has the
   permission, but the convention is local-only edits.
3. **If the upstream has a SKILL.md or AGENTS.md**, prefer that over this
   skill. Upstream doctrine wins.
4. **Don't mirror this fork to `/root/.cline/skills` or `/root/.opencode/skills`.**
   Forks are local-only by convention.

## When this skill does NOT apply

- **Source repos** (non-fork): use `flagships`, `engineering-innovations`,
  `job-app-portfolio`, or a project-specific skill.
- **Public mirrors** of forks: those are sources, not forks. Use the relevant
  family skill.

## Related Skills

- `flagships` — for the 22 source projects
- `engineering-innovations` — for the 195 recent source projects
- `job-app-portfolio` — for the 48 orbit-targeted portfolio repos
- `apex-sovereign-runtime` — for APEX-family doctrine
