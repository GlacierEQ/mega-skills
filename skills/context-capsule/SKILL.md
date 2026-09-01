---
name: context-capsule
description: "Create a compact, current-state capsule that preserves the information needed for the next work chunk without replaying full history. Use before handoffs, resumption, context compaction, delegation, or any complex step requiring focused inputs."
---


# Context Capsule

## Purpose

Protect active work from context drift and overload. This Skill owns the concise current state, not the detailed evidence or full project history.

## Procedure

1. Read the mission, roadmap, evidence register, and most recent handoff.
2. Retain only the current objective, relevant constraints, settled decisions, active artifacts, blocking questions, active risks, and next verification criterion.
3. Replace raw histories with evidence IDs, decision references, or artifact paths.
4. Flag any assumption whose review trigger has been reached.
5. Record environment facts that a future operator must confirm before continuing.
6. Refresh the capsule after meaningful discovery, a phase transition, a failed chunk, or a changed dependency.

## Output contract

Produce `CONTEXT.md` with one current-state snapshot and an exact next action. It must link to detailed material instead of duplicating it.

## Local validation

The capsule passes when a new operator can begin the next chunk after reading it and the named source artifacts, while irrelevant historical narration can remain unloaded.

## Non-goals

Do not use the capsule as a full transcript, a decision archive, or a substitute for evidence registration.

## Compaction Cannot Destroy Source Meaning — 2026-08-31

Context compaction is lossy by design; therefore it is never authoritative over the source layer.

- Before replacing historical narration with IDs, verify that the IDs point to preserved source wording/provenance.
- Carry forward controlling operator/source corrections even when they are not needed for the next technical step.
- If a compacted statement conflicts with a preserved source, flag the capsule as stale and repair the capsule; do not "correct" the source to match the capsule.
- For identity retrieval, retain known aliases/OCR variants and the event fingerprint needed to resume broad search.
- For legal/investigative missions, carry the current allegation universe, highest-value evidence targets, and unresolved contradictions without pruning them merely to save context.
