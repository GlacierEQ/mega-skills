---
id: long-horizon-core
display_name: Long-Horizon Core
schema: ../../schemas/combo-skill.schema.json
version: 0.2.0
status: active
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

## Source-preservation handoff invariant — 2026-08-31

The compound state is an **index and execution layer**, not a replacement archive.

- `EVIDENCE.md` must point to original source records and distinguish source-access state from proposition truth state.
- `CONTEXT.md` may compact history only after stable source IDs/paths preserve the original wording and provenance.
- `HANDOFF.md` must carry any operator/source correction that changes retrieval or interpretation rules.
- A failed or incomplete verification pass may add a retrieval task; it may not erase an existing source assertion.
- For journal/chat sources, preserve original text outside the capsule and label it `REGULARLY KEPT JOURNAL — ORIGINAL WORDING PRESERVED` when that is the mission's source treatment.

## Epistemic contract & Notion bridge — 2026-09-07

Reference-only section (CONTRIBUTING: no skill-level instruction copying into a Combo Skill).

- Contract: `docs/EPISTEMIC_CONTRACT.md` · Mesh: `docs/SKILL_MESH_AND_TOOLS.md`
- Emits: `MISSION.md` / `ROADMAP.md` (PLAN), `EVIDENCE.md` rows (FACT with source-access state ≠ proposition truth state), `CONTEXT.md` (grade-D pointers), gate record + `HANDOFF.md` (OBSERVATION).
- May promote to: a member's output reaches the gate only when evidence-backed; a failed gate returns to the work-packet owner and never silently advances · Proof floor: L2 per artifact, L3 when state files must agree across stores
- Receipts: gate record + `HANDOFF.md` with an exact resume point.
- Contradiction routing: state files that disagree on scope or next action block the handoff; record the disagreement in `EVIDENCE.md` and route to the owner (contract §8). Never erase an existing source assertion.
- PRESERVE (compaction exceptions): original wording and provenance behind every `CONTEXT.md` compaction; `REGULARLY KEPT JOURNAL — ORIGINAL WORDING PRESERVED` labels; operator / source corrections carried in `HANDOFF.md`.
- Mesh edges: COMPOSED_BY → `mega-skills/apex-always-on-core` · VERIFIED_BY → `quality-gate` (member 6) · FEEDS → `handoff-record` (member 7) · GATED_BY → contract §5 (execution-state ladder)
- Tools: the seven member skills in order · durable state files · `schemas/combo-skill.schema.json`
- Notion projection: APEX Always-On Core — Long-Horizon Operating Loop · page `17811a298d2c4d328f293e63ad5a91ca` (route, don't copy — this file outranks the projection)
- Index: `integrations/notion-skill-bridge.json`
