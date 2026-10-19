---
name: receipt-provenance-continuation
description: "Verify provider-native effects, update exact Linear execution cursor and resume safely across sessions without replay."
---

# Receipt Provenance Continuation

## Purpose

Make claimed progress reproducible and prevent already-completed actions from recurring in later chats or worker runs.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Before effect, record exact mission, unique action identity, authorized provider account, target, current source state and expected native proof.
2. After authorized send, recover provider message ID/thread ID and native SENT state; distinguish actual delivery, agency acknowledgment, assignment, production, denial, disposition and remedy from each other.
3. Record source time and observation time separately, mailbox/account, case number, agency identifier and attachments evidence hash where authorized. Never paste passwords, full protected content or identity verification secrets into Linear.
4. Patch only existing canonical issue with verified transition and exact next action, explicitly retiring prior sends or old follow-up checkpoints. Do not mark mission complete because one child action succeeded.
5. Read back both source-native receipt and Linear issue; if either readback fails, mark UNKNOWN/NEEDS_PROOF and preserve cursor for targeted reconciliation rather than blindly repeat.
6. Run cold-resume thought test: independent operator receiving only owning issue and source pointers should know correct beneficiary, what has truly happened, immediate next lawful action and what must not be duplicated.

## Negative and regression tests

- Reject: Create second email after ambiguous timeout
- Reject: Closed issue without substantive human outcome
- Reject: Draft logged as sent
- Reject: Stale source data overwrites recent provider decision

## Output and acceptance

ACTION_RECEIPT.json and RESUME_CURSOR.md containing source proof, exact issue ID, status, limits and next safe action.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
