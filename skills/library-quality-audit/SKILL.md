---
name: library-quality-audit
description: "Reject any capability claim that lacks an admitted, bound, non-stale source. Use as the final gate before a device-capability claim is published or acted on, and whenever a claim set is about to be accepted as evidence."
---

# Library Quality Audit

## Purpose

Accept or reject a claim set against the source record. A claim without a traceable source is not a weaker claim; it is an unverified one. This Skill owns the accept/reject decision and produces the compound audit artifact.

## Procedure

1. Read the claim set and the admitted, bound, and assessed source ids.
2. Map every claim to the source that supports it.
3. Mark any claim whose source is absent from the record as unsupported. Absence of evidence is a fail, not a pass.
4. Decide `pass` only when no unsupported claim remains. Otherwise decide `fail` and list every unsupported claim.
5. Emit `MACBOOK_AIR_LINK_AUDIT.md`.

## Operations

- `claim_mapper` — return claims with their support status
- `source_verifier` — return the source ids present in the record
- `unresolved_claim_lister` — return the unsupported claims
- default — emit the full `MACBOOK_AIR_LINK_AUDIT.md` artifact with the decision

## Output contract

Produce `MACBOOK_AIR_LINK_AUDIT.md` with the overall decision, every claim marked `SUPPORTED` or `UNSUPPORTED`, and an explicit list of unsupported claims.

## Input contract

`claims`: list of `{claim, source_id}`. `sources`/`assessed`/`bound`: the source records to verify against.

## Local validation

The gate passes when a non-creator can trace every published claim to a source that was admitted, bound to an observed property, and pinned to a version and date. A failed gate names each unsupported claim and returns the set to its owner.

## Non-goals

Admitting sources, binding them, and pinning versions are owned by `link-admission`, `machine-binding`, and `staleness-assess`.
