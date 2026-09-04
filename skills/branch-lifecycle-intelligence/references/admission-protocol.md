# Branch Admission and Workstream Protocol

## Purpose

Cleanup alone does not solve branch spread. A healthy system also decides whether a new branch should exist before creating it.

The admission engine uses **explicit workstream identity** as semantic evidence. Branch names remain only a weak similarity signal.

## Request contract

A branch-creation caller supplies:

- `requested_branch`
- `workstream_id`
- optional `continuation_of`
- optional durable `bindings` of known `workstream_id -> branch`

The caller also supplies the latest Branch Lifecycle Plan.

## Decisions

### REUSE_EXISTING

Issued when exactly one live branch is explicitly bound to the workstream, or an explicit `continuation_of` points to a live branch.

The system should update that branch instead of minting another ref.

### REVIEW_CONSOLIDATE

Issued when multiple live branches are explicitly bound to the exact same workstream, or when a continuation conflicts with the durable binding.

New branch creation is blocked until the duplicate stream is resolved.

### CREATE_NEW

Issued when no live explicit binding exists, or when an explicitly continued branch has already reached a closed redundant lifecycle.

### CREATE_NEW_WITH_FAMILY_WARNING

Issued when the requested branch name maps to a similar live family but no semantic workstream binding proves equivalence.

Creation remains allowed because naming is not proof. The warning exists to encourage an operator/agent to inspect the related family before increasing branch count.

### BLOCK

Issued when explicit continuation evidence points to a protected, evidence-blocked, or nonexistent branch.

## Invariants

- Exact workstream binding outranks branch-name similarity.
- Multiple live branches for one exact workstream are a consolidation defect.
- Similar names alone never force reuse.
- A closed lifecycle can justify a fresh branch for genuinely new continuation work.
- Admission decisions are SHA-256 hashed and deterministic from their inputs.
