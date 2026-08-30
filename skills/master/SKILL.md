---
name: master
description: "The master skill \u2014 load this first. Single index and decision tree\
  \ over every skill installed in this workspace. Use when you're unsure which skill\
  \ applies, when starting a new task, or when a request spans multiple domains (memory\
  \ + agents + security + code quality + architecture)."
version: 0.1.0
---

# Master Skill

**Load this first.** This is a router, not a doctrine. It maps the current task
to the right sub-skill. Sub-skills own the substance; this skill owns the choice.

## Decision Tree

Walk top-to-bottom. Stop at the first match.

```
Are you writing or reviewing code?
  ├─ Yes → codemaster (load first; it routes to the rest)
  │        └─ For style/naming/nesting → clean-code
  │        └─ For PR-style review → code-review-checklist
  │        └─ For security-sensitive code → security-review
  │
Are you making an architecture decision?
  └─ Yes → architecture
           └─ For agent topology / tools / planning → ai-agents-architect
           └─ For memory tier choice → agent-memory-systems
           └─ For runtime/receipt/identity (mastermind) → apex-sovereign-runtime
           └─ For a specific project → project skill (see below)
│
Are you building or auditing an agent?
  └─ Yes → ai-agents-architect
           ├─ Designing memory → agent-memory-systems
           ├─ Conversation/chat history → conversation-memory
           ├─ Wiring memory MCP server → agent-memory-mcp
           ├─ Evaluating/testing the agent → agent-evaluation
           └─ Sovereign runtime (mastermind) → apex-sovereign-runtime
│
Are you working in a specific project?
  └─ /root/projects/make-it-heavy → make-it-heavy
  └─ /root/projects/mastermind    → mastermind (+ apex-sovereign-runtime)
  └─ /root/quantum_nexus         → apex-sovereign-runtime + composio
  └─ /root/genesis-prime         → (no project skill — load agent-memory-systems)
  └─ /root/.tower                → (no project skill — load architecture)
│
Are you integrating an external service?
  ├─ Composio (Gmail/Slack/Notion/etc) → composio
  └─ Anything else → check if a project skill lists the adapter
│
Are you following the standard execution protocol?
  └─ Yes → research-study-act
```

## Skill Catalog

### Core engineering

| Skill | Lines | When |
|-------|------:|------|
| `research-study-act` | 32 | Every non-trivial task. Tri-Phase mandate. |
| `clean-code` | 211 | Writing or editing code. Pragmatic Python/JS standards. |
| `code-review-checklist` | 444 | Reviewing a PR or doing a self-audit before merge. |
| `security-review` | 495 | Auth, secrets, user input, payments, sensitive APIs. |
| `architecture` | 57 | Making a structural decision; writing an ADR. |
| `codemaster` | 160 | Coding playbook v2 — 5 task recipes (feature/bug/refactor/review/debug), universal Definition of Done, project test-command table. Load first for any non-trivial code work. |

### Agents

| Skill | Lines | When |
|-------|------:|------|
| `ai-agents-architect` | 90 | Designing an agent: tools, planning loop, memory wiring. |
| `apex-sovereign-runtime` | 375 | Mastermind / APEX-family projects. Receipt chains, identity, lanes. |
| `agent-memory-systems` | 68 | Choosing memory tiers and retrieval strategy. |
| `conversation-memory` | 72 | User-isolated tiered memory for chatbots/assistants. |
| `agent-memory-mcp` | 82 | Wiring the webzler agentMemory MCP server. |
| `agent-evaluation` | 67 | Benchmarking, behavioral tests, reliability metrics. |
| `reasoning-variants` | 136 | ReAct / Plan-and-Execute / Reflection / ToT / Reflexion / Debate — pick the right reasoning loop. |

### Integrations

| Skill | Lines | When |
|-------|------:|------|
| `composio` | 77 | Composio For You or Composio Platform work. |

### Project skills

| Skill | Lines | Project |
|-------|------:|---------|
| `make-it-heavy` | 94 | `/root/projects/make-it-heavy` |
| `mastermind` | 117 | `/root/projects/mastermind` |
| `monolith` | 100 | `/root/projects/monolith` (meta-layer; catalog + propagation) |
| `tower-of-babel` | 130 | `/root/projects/GlacierEQ_Swarm/the-tower-of-babel` (registry-driven; mandatory `tower preflight`) |

### Portfolio / family skills (5)

The GlacierEQ GitHub estate is **1,181 repos** (668 public + 513 private forks).
These 5 family umbrellas cover the whole estate. **Do not write one skill per repo** —
load the family umbrella instead.

| Skill | Scope |
|-------|-------|
| `flagships` | 22 source repos: monolith, mastermind, make-it-heavy, tower-of-babel, apex-control-plane, apex-singularity-head, etc. |
| `job-app-portfolio` | 48 orbit-targeted templated repos (the `*-sentinel`, `*-quantizer` family) |
| `engineering-innovations` | 195 recent non-flagship, non-portfolio source repos (the August 2026 burst) |
| `forks` | 513 private inbound forks of public upstreams |
| `legacy-estate` | 403 older source repos (May 2026 burst, July 2026, etc.) — not actively maintained |

## Load Order (When Multiple Apply)

1. **`research-study-act`** — always, for non-trivial work.
2. **Project skill** — if working inside a known project.
3. **Domain skill** (memory / agents / architecture / security) — picked from the
   decision tree above.
4. **`clean-code`** — implicit on any code change.
5. **`code-review-checklist`** — before declaring done.
6. **`security-review`** — if the change touches auth, secrets, user input, or
   external APIs.

## Common Combinations (Recipes)

| Task | Load in this order |
|------|--------------------|
| Add a new tool to make-it-heavy | `make-it-heavy` → `ai-agents-architect` → `clean-code` → `code-review-checklist` |
| Wire a new memory tier | `agent-memory-systems` → `conversation-memory` → `clean-code` |
| Add a lane to mastermind | `mastermind` → `apex-sovereign-runtime` → `architecture` → `clean-code` |
| Audit memory for privacy/isolation | `conversation-memory` → `agent-memory-systems` → `security-review` |
| Evaluate an existing agent | `agent-evaluation` → `ai-agents-architect` |
| Pick a reasoning loop for a new agent | `ai-agents-architect` → `reasoning-variants` |
| Agent loops / drifts / gives wrong answers | `reasoning-variants` (load `references/99-debugging.md`) |
| Compose multiple reasoning strategies | `reasoning-variants` (load `references/90-composition.md`) |
| Design a new multi-agent system | `architecture` → `ai-agents-architect` → `apex-sovereign-runtime` (if APEX-family) |
| Connect an external service | `composio` → project skill → `security-review` |
| Self-audit of this skill set | `master` (this) → `clean-code` → `code-review-checklist` |
| Add a feature to any project | `codemaster` (load `references/01-add-a-feature.md`) → project skill → `clean-code` |
| Fix a bug | `codemaster` (load `references/02-fix-a-bug.md`) → project skill |
| Refactor | `codemaster` (load `references/03-refactor.md`) → `clean-code` → `code-review-checklist` |
| Review a PR or diff | `codemaster` (load `references/04-review-a-pr.md`) → `code-review-checklist` → `security-review` |
| Debug a test failure | `codemaster` (load `references/05-debug-a-test-failure.md`) → project skill |

## Hard Rules (Always Apply)

1. **Research before code.** Even for "trivial" edits, scan imports and dependents
   first. (See `clean-code` "Before Editing ANY File".)
2. **Verify after change.** Run the project's tests, linter, typecheck. Don't
   claim done without receipts.
3. **User isolation is critical.** Any memory store must scope by `user_id`. No
   exceptions. (See `conversation-memory`.)
4. **No infinite loops.** Every ReAct/Plan-Execute agent must have `max_iterations`.
   Every background process must have a timeout.
5. **Append-only audits.** Receipts, audit logs, memory_audit tables — never
   edit in place. Append a corrective record.
6. **Secrets never leave the vault.** `.vault_env` is production secret material.
   Never log, print, commit, or echo its contents. (See `security-review`.)

## What This Skill Is Not

- Not a substitute for the sub-skills. If a sub-skill exists for the topic,
  load it for the actual patterns and sharp edges.
- Not a tutorial. Use the decision tree; don't read end-to-end.
- Not versioned with the sub-skills. Sub-skills are the source of truth on
  their topic. If they drift, update them; this skill just re-indexes.

## When to Update This File

Add a sub-skill here when:
- You create a new skill in `/root/.agents/skills/<name>/SKILL.md`, AND
- It applies across multiple projects or contexts (not a single project skill).

Project skills (under `/root/projects/<name>/.kilo/skills/` or
`/root/.agents/skills/<project>/SKILL.md`) also belong in the catalog and
in the "Project skills" section.

Remove from this file when:
- The sub-skill is deleted from all install locations
  (`/root/.agents/skills/`, `/root/.cline/skills/`, `/root/.opencode/skills/`).
- The sub-skill is deprecated and superseded by another entry.
