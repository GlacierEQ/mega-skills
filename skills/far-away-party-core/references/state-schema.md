# Durable State Schema

Use these files as the recoverable operating memory for an Expedition or Frontier run. Keep statements factual, concise, dated when time-sensitive, and linked to the governing artifact or evidence. Do not store private credentials, hidden reasoning, or raw transcripts.

## `MISSION.md`

Maintain the stable contract for the work.

| Field | Include |
|---|---|
| Mission | One sentence describing the outcome. |
| Deliverables | Named artifacts, formats, destinations, and owners. |
| Acceptance criteria | Observable checks that determine success. |
| Scope boundary | Explicit inclusions and exclusions. |
| Constraints | User requirements, time, budget, policy, technical, and quality constraints. |
| Stakeholders and approvals | Decision-makers, required reviews, and sensitive-action gates. |
| Skill routing | Primary skill, complementary skills, responsibilities, and handoff artifacts. |
| Assumptions | Bounded assumptions with evidence status and review trigger. |

Update this file only for contract-level changes. Move operational detail to the roadmap or context capsule.

## `ROADMAP.md`

Use an ordered phase table, followed by the current work packet.

| ID | Phase or chunk | Dependency | Owner / role | Status | Gate | Evidence / artifact | Next action |
|---|---|---|---|---|---|---|---|
| P1 | Example: establish mission | — | Integrator | Complete | Contract approved | `MISSION.md` | Start P2 |

Use these statuses exactly: **Not started**, **Active**, **Blocked**, **Ready for review**, **Complete**, or **Superseded**. Never mark a row Complete without its evidence and gate result.

### Current work packet

Write only one active packet unless a real parallel workflow is being coordinated.

| Field | Content |
|---|---|
| Objective | The single result to produce now. |
| Inputs | Exact files, sources, decisions, and constraints to use. |
| Method | Governing skill or procedure and important limits. |
| Output | Artifact or decision expected at completion. |
| Acceptance test | How success will be checked. |
| Authority | Decisions that may be made; decisions that need escalation. |
| State update | Files and rows that must be updated after the chunk. |

## `CONTEXT.md`

Keep this as a compact, current operating capsule. Aim for a short document that can be read at the beginning of every work chunk.

| Section | Include |
|---|---|
| Current objective | Active phase and next atomic chunk. |
| Non-negotiables | Constraints that govern current work. |
| Settled decisions | Decision, rationale summary, evidence pointer, and impact. |
| Active inputs and artifacts | Canonical paths or links only. |
| Open questions and blockers | Owner, deadline or trigger, and impact. |
| Active risks | Likelihood, impact, mitigation, and review trigger. |
| Recent lessons | Reusable facts, failures, quirks, and workarounds. |

Remove obsolete operational detail after recording its enduring lesson or evidence pointer. Preserve decisions that constrain downstream work.

## `EVIDENCE.md`

Use a register rather than narrative notes. Distinguish facts from conclusions.

| ID | Claim or requirement | Evidence type | Source / artifact | Date or version | Validation result | Limitations |
|---|---|---|---|---|---|---|
| E-01 | Example: output meets test X | Test run | `tests/result.txt` | v1 | Pass | Test scope excludes Y |

Record external source URLs, versioned artifacts, test results, review notes, and user approvals. Flag unverified claims explicitly.

## `HANDOFF.md`

Rewrite this at every durable handoff. It must allow another operator to resume without replaying the entire conversation.

| Section | Include |
|---|---|
| Status snapshot | Current phase, completed work, and high-level health. |
| Exact resume point | The first concrete action to perform next. |
| Required reading order | State files and artifacts to open before continuing. |
| Validated environment | Relevant paths, versions, commands, or session facts that were actually confirmed. |
| Active blockers | What is blocked, why, impact, and required owner or approval. |
| Recent decisions | Decisions since the last handoff and their evidence pointers. |
| Verification state | Tests run, results, and tests still required. |
| Cautions | Irreversible actions, sensitive steps, known failure modes, and instructions not to repeat. |

## Compaction protocol

Run compaction at a phase boundary, before a large context switch, after a research burst, before delegation, and before ending an unfinished run.

1. Update `EVIDENCE.md` with newly verified sources, tests, and artifacts.
2. Update `ROADMAP.md` statuses, dependencies, gates, risks, and the one exact next chunk.
3. Distill only reusable decisions, active constraints, unresolved questions, and lessons into `CONTEXT.md`.
4. Rewrite `HANDOFF.md` so a fresh operator can orient, verify the environment, and act.
5. Confirm the next chunk can proceed from the state files without requiring a raw conversation replay.

If a state file disagrees with a verified artifact, correct the state file and record the discrepancy as a lesson. The validated artifact and its evidence are authoritative.

## Resume protocol

1. Read `HANDOFF.md`, then `MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, and the evidence entries cited by the current work packet.
2. Verify that referenced artifacts, environment assumptions, and external dependencies still exist.
3. Reconfirm blocked approvals or time-sensitive facts when required.
4. Continue only from the recorded next action; revise the roadmap first if new information invalidates it.
5. Do not repeat completed work unless the evidence is missing, stale, contradicted, or fails a current acceptance test.
