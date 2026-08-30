---
name: long-horizon-core
description: 'Combo Skill: Long-Horizon Core. Reusable capability chain.'
---

# Long-Horizon Core

## Purpose and selection

Use this Combo Skill when a mission has dependent phases, durable artifacts, material uncertainty, or a need for safe resumption. Do **not** use it to inflate a simple bounded response.

## Incremental value

This Combo turns seven independent governance Skills into one repeatable operating loop. It adds the ordering, handoff discipline, and state consistency required for a future Mega Skill to route work safely.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `mission-contract` | Mission request and constraints | `MISSION.md` | Outcome, scope, approvals, and criteria are explicit. |
| 2 | `roadmap-builder` | `MISSION.md` | `ROADMAP.md` | Dependencies and phase gates are explicit. |
| 3 | `evidence-register` | Sources, tests, and artifacts | `EVIDENCE.md` | Material claims map to evidence or assumptions. |
| 4 | `context-capsule` | Mission, roadmap, and evidence | `CONTEXT.md` | Next chunk is actionable without raw history. |
| 5 | `work-packet` | Current chunk and constraints | Work packet | Owner, output, authority, and test are explicit. |
| 6 | `quality-gate` | Artifact, evidence, and criteria | Gate record | Acceptance is reproducible. |
| 7 | `handoff-record` | Validated state and gate | `HANDOFF.md` | Safe resumption point is exact. |

## Handoff contract

`MISSION.md` is the sole input to planning; `ROADMAP.md` and `CONTEXT.md` define the work packet; only evidence-backed artifacts reach the gate; the gate record and verified state feed the handoff. A failed gate returns to the work-packet owner, never silently advances.

## Compound output

**Artifact:** `long-horizon-run-state.md`, comprising the five durable state files plus the current work packet and gate record.

**Ready for Mega Skill integration when:** the state files agree on scope and next action, every open assumption has a review trigger, and the next route can consume named evidence rather than raw conversation history.
