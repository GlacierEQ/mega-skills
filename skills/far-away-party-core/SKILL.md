---
name: far-away-party-core
description: Establish a context-preserving, evidence-driven operating method for complex work. Use as the atomic operating skill inside an approved Combo or Mega Skill, or directly when a mission needs durable state, verifiable chunks, phase gates, and recoverable handoffs.
---

# Far Away Party Core

## Purpose

Use Far Away Party Core as the **atomic operating layer** for difficult work that must travel from an initial request to a verified result across many steps, files, tools, or specialist skills. It does not replace domain skills. It provides the routing, durable memory, execution cadence, integration, and quality controls that let those skills work together reliably.

Apply it when a task has any of these traits: multiple dependent phases; uncertainty that must be reduced through research or inspection; several deliverables; a need to resume after interruption; specialist work that benefits from delegation; material risk of context drift; or a request for exceptional thoroughness. Do not use it to inflate a simple, bounded reply.

> **Core rule:** Externalize the task state, execute one verifiable chunk at a time, and make every handoff recoverable.

## Non-negotiable operating rules

1. **Route before acting.** Identify the task shape, governing constraints, relevant specialist skills, needed tools, and final acceptance criteria before starting irreversible work.
2. **Treat durable artifacts as the source of truth.** Keep the current mission, roadmap, key decisions, evidence, and handoff status in the run workspace. Do not rely on conversational memory alone.
3. **Use structured decision records, not hidden reasoning.** Record concise conclusions, evidence, alternatives considered, confidence, and the next review trigger. Preserve only what a future operator needs.
4. **Work in bounded chunks.** Every chunk must have one concrete objective, limited inputs, an owner or role, a deliverable, and a verification check.
5. **Verify at phase boundaries.** Do not advance merely because work was attempted. Advance when the stated gate is met or an explicitly documented exception is approved.
6. **Preserve truthfulness.** Never claim a test, source review, delegation, or action occurred unless it occurred. State uncertainty and blockers plainly.
7. **Spend context deliberately.** Load only the current state capsule and the references required for the present chunk. Compact stale detail into durable summaries before it crowds out active work.

## Choose the run mode

| Mode | Use when | Required structure |
|---|---|---|
| **Direct** | The task is simple, bounded, and can be completed in one short pass. | Apply a light contract and verify the answer. |
| **Expedition** | The task needs several dependent steps, research, artifacts, or a quality pass. | Create a mission, roadmap, and handoff record; execute sequential chunks. |
| **Frontier** | The task is long-running, ambiguous, cross-domain, high consequence, or needs multiple specialists. | Use the full durable-state system, phase gates, integration cadence, and swarm protocol. |
| **Resume** | A Far Away Party workspace or prior project evidence exists. | Read `HANDOFF.md`, `MISSION.md`, `ROADMAP.md`, and `CONTEXT.md` before doing new work. |

Escalate from Direct to Expedition or Frontier as soon as the scope, uncertainty, or artifact count warrants it. Do not silently downgrade a Frontier run merely because a single chunk appears easy.

## Set up the run

For Expedition or Frontier work, create a dedicated run workspace in the project or task directory. Copy the files in `templates/` as the initial state. Use the following state files:

| File | Purpose | Update when |
|---|---|---|
| `MISSION.md` | Objective, constraints, stakeholders, acceptance tests, and scope boundary. | The user changes scope or a constraint becomes known. |
| `ROADMAP.md` | Ordered phases, dependencies, statuses, gates, risks, and the next atomic chunk. | A chunk starts, completes, fails, or changes a dependency. |
| `CONTEXT.md` | Compact current-state capsule: decisions, assumptions, open questions, active artifacts, and active risks. | At every meaningful handoff and after significant discoveries. |
| `EVIDENCE.md` | Source register, test evidence, artifact inventory, claims, and verification links. | A source, test, result, or deliverable is added. |
| `HANDOFF.md` | Exact resume point, completed work, commands or locations, unresolved blockers, and first next action. | Before interruption, delegation, context compaction, or final delivery. |

Read [state-schema.md](references/state-schema.md) before creating or compacting a Frontier workspace. Use the supplied templates rather than inventing incompatible state files.

## Compose complementary skills

First identify the **primary domain skill** that governs the main deliverable. Then add only the complementary capabilities that close a genuine gap, such as research, data analysis, design, document production, implementation, deployment, or validation. Keep a skill-routing record in `MISSION.md` or `ROADMAP.md` that names each skill, its responsibility, its required inputs, and its output artifact.

Use this precedence order when guidance conflicts: applicable safety and platform requirements; explicit user constraints; the primary domain skill; a directly relevant specialist skill; then this coordination skill. Far Away Party coordinates the workflow but must never override a more specific mandatory procedure.

Read [skill-routing.md](references/skill-routing.md) when choosing a primary skill, defining ownership, or resolving a cross-skill handoff.

## Execute the long-horizon workflow

### 1. Establish the mission contract

Translate the request into a testable outcome. Define what will be delivered, what is excluded, what evidence proves success, constraints, dependencies, approvals, and the stop condition. Resolve a material ambiguity before expensive or irreversible work; otherwise, record a bounded assumption and its review trigger.

### 2. Build a dependency-aware roadmap

Decompose the mission into phases and then into atomic chunks. Put uncertainty-reduction, safety checks, architecture decisions, and other high-leverage risks before routine production work. Each chunk must be small enough to complete and verify without requiring the entire task to remain in active context.

For the full phase-gate model and chunk format, read [operating-protocol.md](references/operating-protocol.md).

### 3. Create a minimal active context capsule

Before each chunk, refresh `CONTEXT.md` to contain only the current objective, relevant constraints, settled decisions, required inputs, active artifacts, blocking questions, and the next verification criterion. Link to detailed evidence rather than duplicating it. Load this capsule and only the primary-skill materials needed for the chunk.

### 4. Allocate work intentionally

Use one executor for serial, dependent work. When independent workstreams genuinely exist, use a **scout–specialist–verifier–integrator** pattern: scouts reduce uncertainty; specialists create bounded artifacts; verifiers test requirements independently; the integrator reconciles results into the durable state. Do not create duplicate work or claim parallel execution when the environment is sequential.

Give every assignment a work packet with a task boundary, inputs, expected artifact, acceptance test, decision authority, and required state update. Read [swarm-protocol.md](references/swarm-protocol.md) before assigning or integrating multiple workstreams.

### 5. Run the chunk loop

For each chunk, follow this sequence:

1. **Orient:** Read the active context capsule, relevant work packet, and only necessary source material.
2. **Act:** Complete the bounded action with the governing specialist skill and appropriate tools.
3. **Verify:** Run the promised test, inspect the artifact, cross-check the claim, or obtain the required approval.
4. **Assimilate:** Record the result, evidence, decisions, failures, and changed assumptions in the state files.
5. **Replan:** Set the exact next atomic chunk, update dependencies and risks, and determine whether the phase gate has passed.

If a chunk fails, classify the failure as missing input, invalid assumption, technical defect, external block, quality failure, or scope conflict. Preserve the lesson in `CONTEXT.md` and revise the roadmap instead of repeatedly retrying the same approach.

### 6. Apply quality gates

At the end of each phase, compare the artifact and evidence against the mission contract. Confirm completeness, correctness, consistency, traceability, usability, and safety or policy compliance as applicable. Use a reviewer who did not create the artifact whenever independence materially improves confidence.

### 7. Compact and resume safely

Compact frequently enough that the active capsule remains concise. Preserve decisions, evidence pointers, completed statuses, failures, and the next action; discard only transient narration that has no future operational value. Before resuming a run, read the handoff and state files, validate that the environment and referenced artifacts still exist, then continue from the recorded next action.

### 8. Integrate and deliver

Perform a final requirements trace from every acceptance criterion to supporting evidence. Reconcile specialist outputs into one coherent result, remove duplicated or contradictory material, and present the requested deliverables with material limits and residual risks. Mark the run complete only after the delivery criteria and final quality gate pass.

## Guardrails for excellence and efficiency

Use high effort where it changes the answer: mission framing, risk reduction, evidence collection, key decisions, integration, and verification. Avoid expensive repetition where it does not: reload compact state instead of raw histories; cite canonical artifacts instead of copying them; batch truly independent discovery; and stop research when the acceptance threshold is met.

Treat confidence as a claim that requires support. Distinguish observed facts, derived conclusions, assumptions, and open questions. When evidence is insufficient, offer a bounded next step instead of manufacturing certainty.

Never let autonomy bypass required user approval, sensitive actions, payments, external publication, deletion, or a policy-required confirmation. Record the approval requirement as a blocking gate in the roadmap.

## Reference map

| Need | Read this resource |
|---|---|
| Create, update, compact, or resume durable task state | [state-schema.md](references/state-schema.md) |
| Decompose work, define phase gates, or evaluate a chunk | [operating-protocol.md](references/operating-protocol.md) |
| Delegate, coordinate, or integrate focused workstreams | [swarm-protocol.md](references/swarm-protocol.md) |
| Select and hand off between complementary skills | [skill-routing.md](references/skill-routing.md) |
| Initialize a new run workspace | `templates/MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` |

## Completion checklist

Before closing a Far Away Party run, confirm that the mission contract is satisfied or an explicit exception is recorded; every material claim maps to evidence; all requested artifacts are present and accessible; phase gates and final validation passed; the user-facing delivery states limits and next actions where relevant; and `HANDOFF.md` leaves a future operator an accurate recovery point.
