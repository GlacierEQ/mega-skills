---
name: linear-ops
description: >
  Operate Linear as a shared ops queue for any AI agent. Use when the user asks
  to create, update, triage, clean, or analyze Linear issues, projects, labels,
  or WIP, or when work needs a durable next-action ticket without dumping sealed
  case strategy into the tracker. Covers protected-layer field rules, cleanup
  playbooks (PR mirrors, priority inflation, WIP caps), and connector-safe
  patterns. Do not use for writing legal theories into issue bodies or for
  storing credentials, minor identifiers, or medical facts in Linear.
metadata:
  short-description: Portable Linear ops queue for any AI — protected fields, cleanup, triage
  version: "1.0.0"
  kind: atomic
  team_default: Hi-classhomeservices
user-invocable: true
---

# linear-ops

Linear is the **ops queue**, not the case file. Any agent that can call Linear
APIs or MCP tools must follow this skill so tickets stay useful and not careless.

## When to activate

- Create / update / triage / close Linear issues
- Workspace cleanup, WIP review, priority rebalance
- GitHub PR mirror hygiene
- n8n or other automation that opens Linear tickets on errors
- User says "Linear", "issue tracker", "ticket this", "clean the board"

## Connector contract (no baked secrets)

- Prefer the host's Linear connector / MCP tools (list/save issues, teams, labels).
- Never embed API keys in this skill, in issue bodies, or in commits.
- If the host has no Linear tool, output a **ready-to-paste ops ticket** (title +
  markdown body) that obeys the schema — do not invent tool success.
- Default team when none named: `Hi-classhomeservices` (key `HI`). Confirm if
  multiple teams exist.

## Protected layer — hard stops

| Allowed in Linear | Forbidden without explicit operator override |
|---|---|
| Workflow/repo name, execution id, failing node | Minor names, DOB, school, medical detail |
| Ops next action, blocker, owner, due date | Sealed legal theory, full pleading strategy |
| Public docket numbers already public | Credentials, tokens, session cookies |
| Links to private docs **by title only** | Pasting secret doc contents into description |

If the user asks to put forbidden material in an issue, refuse that field, keep
ops facts, and suggest Box/Drive/private note instead.

Full field rules: [references/issue-schema.md](references/issue-schema.md).

## Core loops

### 1) Create issue

1. Resolve team (named team or default).
2. Title ≤ 90 chars, verb-led ops outcome (`Rotate n8n MCP token`, not essays).
3. Body uses the ops template in the schema reference.
4. Priority — see policy below. Do not default everything to High.
5. Labels — reuse existing (`Chain Step`, `Connector`, mission labels). Do not
   invent label spam.
6. Create only when the user asked to create or approved a draft.

### 2) Triage / update

1. Read current status, assignee, parent, labels.
2. Change only requested fields. Prefer append notes over rewriting history.
3. Moving to Done requires a one-line completion note (what shipped or why closed).

### 3) Cleanup pass

Follow [references/cleanup-playbook.md](references/cleanup-playbook.md).
Default order:

1. PR mirror cluster (merged/closed upstream → Done or Canceled)
2. Hide/filter completed in views (do not reopen)
3. Cap In Progress (recommend ≤ 8 true WIP)
4. Deflate priority inflation
5. Supersede duplicate P0/template steps only with explicit approval on mission parents

**Never mass-close Mission KEKOA / CHERRY / 1FDV parents without explicit approval.**

### 4) Analyze board (read-only)

When asked to analyze without editing:

1. List teams, issues (status, project, labels, updatedAt, priority).
2. Cluster — PR mirrors, Done noise, template `[n/m]` steps, CHAIN parents, stale WIP.
3. Return counts + ranked cleanup actions. Do not mutate unless asked.

Optional local helper (no network): pass a JSON issue export to
`scripts/analyze_board.py` for the same clusters offline.

## Priority policy

| Level | Use when |
|---|---|
| Urgent (1) | External deadline or safety within ~7 days |
| High (2) | Active mission next human action |
| Medium (3) | Blocked on dependency / chain step waiting |
| Low (4) | Hygiene, PR mirrors, research |
| None (0) | Parking lot |

If more than ~40% of open issues are High or Urgent, say so and propose deflation.

## WIP policy

- Recommend ≤ 8 issues In Progress per operator.
- Parent CHAIN stays In Progress only if a child has a next action this week.
- Otherwise demote parent to Todo with blocker one-liner.

## Relation to other skills

- **n8n-automation** — automation plane; Linear tickets from failures stay ops-only.
- **agent-memory-*** — memory is read-first; do not mirror sealed memory into Linear.
- Case/docket skills own evidence; Linear only tracks the **next ops move**.

## Done means

- Requested Linear action completed **or** a paste-ready ticket delivered if no connector
- Protected-layer rules respected
- Cleanup mutations scoped and reported (ids + new status)
- No secrets printed

## Anti-patterns

- Dumping full case chronology into every child issue
- Creating a new epic for cleanup when status edits suffice (especially near issue limits)
- Leaving merged GitHub PR mirrors In Progress
- Marking everything High
- Silent archive/delete of mission parents
