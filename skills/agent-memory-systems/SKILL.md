---
name: agent-memory-systems
description: "Durable agent continuity, source-realized hydration, provenance-bound memory, and logical progress. Use when an agent must resume existing work without reconstructing it from summaries, preserve resolved state and contradictions, bind verified transitions to evidence, or coordinate memory across peer providers."
---

# Agent Memory Systems — Continuity Engine

Memory is not merely storage and it is not merely retrieval.

For long-running agentic work, the real requirement is:

> **A fresh worker must be able to recover the nearest valid continuation state and advance it without reconstructing the project from prose.**

This skill provides the continuation substrate for that behavior.

It preserves the useful foundations of agent memory—working memory, episodic memory,
semantic memory, procedural memory, retrieval, temporal relevance, chunking, embeddings,
and provider-specific storage—while adding a stronger operational layer:

**SOURCE-BEARING STATE → HYDRATION → CRITICAL PATH → EXECUTION → VERIFICATION → DURABLE CONTINUATION**

## Prime Laws

### 1. Boot context routes retrieval; it does not replace retrieval

Startup summaries, injected context, memory summaries, indexes, manifests, checkpoints,
cached descriptions, and previous assistant prose are orientation hints.

They are not automatically:

- current project state;
- current repository state;
- current provider state;
- controlling architecture;
- proof of execution;
- proof that an artifact still exists;
- proof that a previously observed fact remains current.

Use boot context to locate the living state.

Then hydrate the materially relevant sources.

### 2. Continue from the nearest valid state

Do not restart merely because the current worker is fresh.

The default continuation question is:

> **What exact work is being continued, what is the last verified state, what materially remains unresolved, and what action advances it now?**

Use only enough retrieval to answer that question reliably.

`CONTINUE != REDISCOVER`

`HYDRATE != RECONSTRUCT FROM SCRATCH`

### 3. Memory is a projection, not a throne

No continuation file, memory provider, vector store, repository, database, summary,
manifest, or index becomes universal truth merely because it is convenient.

Represent qualified systems as source-bearing peer projections.

Preserve:

- provider identity;
- resource locator;
- revision;
- content hash when available;
- observation time;
- truth state;
- scope of what the source actually establishes;
- typed relationships;
- contradictions;
- supersession;
- lineage.

A continuation projection is a resumable source map.

It is **not** a canonical truth authority.

### 4. Operator knowledge and external verification are different truth surfaces

Operator intent controls mission direction, scope, priorities, framing, and architecture
decisions.

Operator firsthand observations are primary source material for the operator's own
experience and intent.

External sources establish externally verifiable facts within their supported scope.

Execution receipts establish execution state.

Do not silently collapse these into one category.

### 5. Verified progress requires a receipt

A material state transition uses:

**BEFORE STATE → ACTION → OBSERVED RESULT → AFTER STATE → EVIDENCE**

Attempted execution is not completed execution.

Generated is not executed.

Executed is not verified.

Committed is not deployed.

Deployed is not observed in operation.

Every `behavior_verified` transition must reference source-bearing evidence.

### 6. Resolved questions stay resolved

A settled question must not continually re-enter the critical path because a fresh
worker lacks context.

Preserve the resolution and its evidence.

Reopen it only through an explicit operation with a material reason, such as:

- new contradictory evidence;
- changed underlying state;
- invalidated verification;
- downstream failure demonstrating the assumption was wrong;
- explicit operator reopening.

### 7. Contradictions are first-class state

Never erase a conflict simply to produce a clean summary.

Preserve both claims, their source references, and the contradiction itself.

Resolution adds a new state; it does not rewrite history.

### 8. Logical progress controls execution

For active work:

**CURRENT VERIFIED STATE  
→ NEXT MATERIAL DEPENDENCY  
→ STRONGEST AVAILABLE ACTION  
→ EXECUTE  
→ READ BACK  
→ TEST  
→ REPAIR  
→ VERIFY  
→ PERSIST  
→ NEXT DEPENDENCY**

Research, auditing, inventorying, planning, documentation, refactoring, and scanning
are progress only when they materially advance the active mission.

If an executable repair/build action is available, do not substitute another report
for execution.

### 9. Discovery does not automatically expand scope

Newly visible opportunities are not automatically on the critical path.

If a discovery is required for the active mission, incorporate it.

Otherwise preserve it as a continuation opportunity and keep moving toward the active
target.

### 10. Persistence is part of execution

An in-memory mutation is not durable continuation state.

The required sequence is:

**MUTATE → ATOMIC SAVE → INTEGRITY REBIND → READ/HYDRATE**

The runtime uses a SHA-256 digest over the projection and links each saved snapshot to
the previous digest.

A stale digest means the projection is dirty, corrupt, or has been altered outside the
expected persistence path.

Fail closed rather than hydrating it as durable truth.

---

# Continuation Projection

The machine-readable contract lives in:

`resources/agent_memory_systems_schema.json`

Default portable projection path:

`.glaciereq/continuation.json`

The path is a convention, not a universal authority location.

A projection contains:

## Mission

- `mission_id`
- `operator_intent`
- `active_target`
- `status`
- `scope`

## Continuation

- `last_verified_state`
- `critical_path`
- `next_action`
- completed work
- blockers
- resolved questions

## Source pointers

Each source carries:

- stable local `source_id`
- provider
- locator
- scope
- truth state
- observed time
- revision where available
- content hash where available

## Transition receipts

Each material verified transition records:

- before state
- action
- observed result
- after state
- evidence references
- verification time

## Contradictions

Conflicting source-backed claims remain explicit until resolution.

## Peer projections

Other provider- or repository-side views can be linked as:

- `peer`
- `projection`
- `derived_from`
- `supersedes`
- `superseded_by`
- `corroborates`
- `contradicts`

## Lineage and integrity

Every persisted projection includes:

- `state_digest`
- `previous_digest`
- creation timestamp
- update timestamp

This gives the next worker an integrity-bound continuation cursor.

---

# Hydration Packet

`hydrate` does not dump the entire historical corpus into context.

It emits the compact state required to resume:

- mission;
- last verified state;
- critical path;
- strongest next action;
- open blockers;
- resolved questions;
- open contradictions;
- source pointers;
- peer projections;
- recent transition receipts;
- projection digest.

The packet explicitly instructs the worker to retrieve materially required live sources
before relying on them for current external state.

This prevents two opposite failures:

1. reconstructing everything from scratch;
2. treating the summary packet as the living system.

---

# CLI

The executable entrypoint is:

```bash
python skill.py <command> ...
```

## Initialize

```bash
python skill.py init .glaciereq/continuation.json \
  --mission-id "repo-upgrade" \
  --intent "Continue the existing implementation without reconstruction." \
  --target "Ship and verify the current upgrade."
```

## Validate

```bash
python skill.py validate .glaciereq/continuation.json
```

Validation checks both structure and integrity digest.

## Hydrate

```bash
python skill.py hydrate .glaciereq/continuation.json
```

Use this at worker startup or task continuation.

## Attach a source

```bash
python skill.py add-source .glaciereq/continuation.json \
  --provider github \
  --locator "GlacierEQ/example@abc123" \
  --scope "implementation and test evidence" \
  --truth-state behavior_verified \
  --revision abc123 \
  --source-id src-github-main
```

## Set the critical next action

```bash
python skill.py set-next .glaciereq/continuation.json \
  --action "Run the integration test against the repaired implementation." \
  --why "Unit behavior is verified; integration is the next unresolved dependency." \
  --critical-path "integration test" \
  --critical-path "deployment readback"
```

## Record a verified transition

```bash
python skill.py transition .glaciereq/continuation.json \
  --action "Run integration test" \
  --result "Integration suite passed against revision abc123." \
  --after-state "integration behavior verified" \
  --evidence-ref src-github-main \
  --completed-description "Integration behavior verified" \
  --next-action "Deploy to the bounded staging environment." \
  --next-why "Integration is complete; staging observation is the next dependency."
```

## Complete a mission

```bash
python skill.py complete .glaciereq/continuation.json \
  --final-state "requested outcome verified complete" \
  --evidence-ref src-final-receipt
```

Completion clears the executable next-action tail.

---

# Memory Architecture

The continuation layer does not replace normal memory systems.

Use the appropriate memory mechanism for its job.

## Working / short-term memory

Use for:

- active reasoning;
- immediate tool outputs;
- temporary execution context;
- transient hypotheses.

Do not confuse context-window presence with durable continuation.

## Episodic memory

Use for:

- events;
- prior execution passes;
- operator interactions;
- incidents;
- experiments;
- historical observations.

Link important episodes into the continuation projection by source pointer rather than
copying the entire episode.

## Semantic memory

Use for:

- durable concepts;
- architecture knowledge;
- stable relationships;
- learned technical facts;
- domain models.

Preserve provenance where a semantic fact depends on a source.

## Procedural memory

Use for:

- skills;
- workflows;
- tool procedures;
- recovery routines;
- deployment sequences;
- verification methods.

Procedural memory tells the worker **how** to act.

Continuation state tells it **where the work currently is**.

## Vector retrieval

Vector stores are useful retrieval surfaces, not truth authorities.

Track:

- embedding model;
- chunk strategy;
- source identity;
- timestamps;
- metadata filters;
- retrieval tests;
- conflict handling.

A high-similarity result is a retrieval candidate, not proof.

---

# Behavioral Anti-Patterns

## ❌ Summary-First Boot

Reading one boot summary and proceeding as if the project is hydrated.

## ❌ Full Reconstruction

Rebuilding the entire architecture every time a worker starts.

## ❌ Canonicalization by Convenience

Making whichever provider was easiest to query the master truth.

## ❌ Resolved-State Amnesia

Reopening completed or settled questions because the current context window lacks the
original evidence.

## ❌ Dirty-State Hydration

Mutating a projection in memory and hydrating from it before persistence and digest
rebind.

## ❌ Evidence-Free Progress Claims

Advancing `last_verified_state` without a source-backed receipt.

## ❌ Endless Archaeology

Continuing retrieval after enough source-bearing state exists to execute the next
material dependency.

## ❌ Scope Capture

Letting newly discovered improvements replace the operator's active target.

## ❌ Provider Flattening

Copying facts across systems while dropping source identity, revisions, hashes,
timestamps, or contradictions.

---

# Required Worker Boot Sequence

For continuity-dependent work:

1. Read the current operator request.
2. Locate the relevant continuation projection(s).
3. Validate projection integrity.
4. Hydrate the compact continuation packet.
5. Retrieve only materially required source-bearing live state.
6. Preserve contradictions and peer provenance.
7. Determine the nearest valid continuation point.
8. Identify the next material dependency.
9. Execute the strongest available action.
10. Read back and verify the resulting state.
11. Persist the updated continuation projection.
12. Continue until the requested active unit is complete or genuinely blocked.

The objective is not perfect recall.

The objective is:

> **A living system whose work compounds across workers without forcing the operator to rebuild the context every time.**
