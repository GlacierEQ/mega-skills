---
name: mega-agent-memory-systems
description: "Composed memory and continuity surface for durable agent work. Routes source-realized hydration and continuation execution through agent-memory-systems and behaviorally verifies persistence, integrity, source binding, and hydration before claiming readiness."
---

# MEGA-AGENT-MEMORY-SYSTEMS

This Mega Skill is the **composition surface** for agent memory.

It does not create a second memory brain.

The substantive continuation engine lives in:

`../agent-memory-systems`

The Mega Skill composes that engine with broader memory architecture and exposes a
single operator-facing entrypoint.

## Governing Objective

A fresh worker should be able to:

1. locate durable continuation state;
2. validate its integrity;
3. hydrate the nearest valid continuation cursor;
4. retrieve materially required live sources;
5. identify the next unresolved dependency;
6. execute logical progress;
7. verify the resulting state;
8. persist a stronger continuation point.

The worker should **not** reconstruct the project from summaries.

## Composition Law

`mega-agent-memory-systems` owns composition.

`agent-memory-systems` owns continuation execution.

Do not duplicate the continuation implementation inside this Mega Skill.

Do not create another canonical memory authority.

Memory providers, repositories, databases, and continuation files remain qualified
peer projections with provenance.

## Truthful Verification

This Mega Skill must never claim behavioral verification from:

- hashing Markdown;
- counting scripts;
- checking that a file exists;
- checking that a registry entry exists;
- receiving a successful process launch;
- generating a projection without reading it back.

`VERIFIED` means behavior was actually exercised.

The verification command performs:

**CREATE PROJECTION  
→ BIND SOURCE  
→ BIND PEER PROJECTION  
→ ATOMIC PERSIST  
→ INTEGRITY RELOAD  
→ RECORD SOURCE-BACKED TRANSITION  
→ PERSIST NEW DIGEST  
→ RELOAD  
→ HYDRATE  
→ ASSERT CONTINUATION CURSOR**

Only a successful round-trip returns:

`BEHAVIOR_VERIFIED`

Failure returns:

`FAILED`

## Commands

### Verify the memory/continuation composition

```bash
python skill.py verify --json
```

The receipt includes:

- behavioral status;
- continuation schema version;
- projection digest;
- previous digest;
- verification receipt id;
- exact checks performed;
- atomic engine path.

### Initialize durable continuation

```bash
python skill.py init .glaciereq/continuation.json \
  --mission-id "active-mission" \
  --intent "Continue existing work without reconstruction." \
  --target "Reach the requested verified outcome."
```

### Hydrate

```bash
python skill.py hydrate .glaciereq/continuation.json
```

### Validate

```bash
python skill.py validate .glaciereq/continuation.json
```

### Add source-bearing state

```bash
python skill.py add-source .glaciereq/continuation.json \
  --provider github \
  --locator "GlacierEQ/repo@revision" \
  --scope "implementation state" \
  --truth-state inspected
```

### Advance the critical path

Use `set-next`, `transition`, and `complete` through this Mega Skill exactly as exposed
by `agent-memory-systems`.

## Boot Contract

For continuity-dependent work:

**OPERATOR REQUEST  
→ CONTINUATION PROJECTION  
→ INTEGRITY CHECK  
→ HYDRATION PACKET  
→ MATERIAL LIVE SOURCE RETRIEVAL  
→ NEAREST VALID STATE  
→ CRITICAL PATH  
→ EXECUTION  
→ READBACK  
→ TEST  
→ REPAIR  
→ VERIFY  
→ PERSIST**

Startup summaries and injected text are routing hints only.

They do not outrank source-bearing current state.

## Memory Surfaces

The continuation engine complements rather than replaces:

- working memory;
- episodic memory;
- semantic memory;
- procedural memory;
- vector retrieval;
- provider-specific memory stores;
- repositories;
- files;
- databases;
- external systems.

The correct relationship is:

**MEMORY LOCATES → SOURCES ESTABLISH → EXECUTION CHANGES → VERIFICATION PROVES → CONTINUATION PRESERVES**

## Polycentric State

Do not force a universal master truth merely because multiple providers disagree.

Preserve:

- provider identity;
- exact locator;
- revision/hash;
- observation time;
- truth-state scope;
- contradictions;
- supersession;
- peer relationships.

A continuation projection tells the next worker **where to resume**.

It does not erase the underlying systems.

## Resolved State

Resolved questions remain resolved unless explicitly reopened for a material reason.

A new worker lacking context is **not** itself a material reason.

## Logical Progress

Hydration is complete when enough source-bearing state exists to execute the next
material dependency safely and correctly.

Do not keep retrieving merely because more history exists.

Do not stop at an audit when executable repair is available.

Do not let discovery silently replace the active mission.

The operating loop is:

**CURRENT VERIFIED STATE  
→ NEXT MATERIAL DEPENDENCY  
→ EXECUTE  
→ VERIFY  
→ PERSIST  
→ CONTINUE**

## Definition of Success

This Mega Skill succeeds when memory behaves as **continuity infrastructure** rather
than narrative recall.

The proof is not that the system can describe prior work.

The proof is that another worker can **resume the work correctly from durable state and
move it forward**.
