---
name: linear-frontier-deduplicator
description: "Reconcile live provider truth against the existing Linear work graph and prohibit replay of already verified external effects."
---

# Linear Frontier Deduplicator

## Purpose

Keep the canonical execution issue accurate and actionable without creating parallel boards or replaying external requests.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Recover current mission root, binding, owning action issue, aliases, provider IDs, comments, exact relationships, newest corrections and resume cursor before selecting an update.
2. Construct the action identity from mission, beneficiary, responsible custodian, requested legal or business effect, source period and prior provider thread ID; distinct evidence exhibits for the same request are not new actions.
3. Search issue titles/descriptions and receipts for same intent and recipient; compare newest external events against stale issue text. Reuse owning issue, append attributed correction rather than destructively rewriting history.
4. Classify candidate action as NOT_YET_DONE, VERIFIED_DONE, WAITING_EXTERNAL, NEEDS_PROOF, PARTIAL, SUPERSEDED, or BLOCKED. Ambiguous API send or timeout is NEEDS_PROOF, never automatic retry.
5. Update only source-bound operational cursor; keep historical receipts and unrelated case lanes intact. Link related proceedings instead of combining separate legal identities, case numbers or custodians.
6. Read back the issue and check exact marker, source IDs, next justified act, date provenance and no duplicate created; independently check external provider before claiming an effect.

## Negative and regression tests

- Reject: Duplicate Gmail notice after prior SENT
- Reject: Repeated police filing after approved report number
- Reject: Court-facing draft mistaken for JEFS filing
- Reject: Case plan from one docket overwrites another case

## Output and acceptance

LINEAR_RECONCILIATION.md with canonical issue ID, stable work/action identity, provider citations, retired tasks, active branches and next evidence test.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
