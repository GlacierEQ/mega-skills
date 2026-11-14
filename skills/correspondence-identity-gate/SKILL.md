---
name: correspondence-identity-gate
description: "Resolve first-party sender, beneficiary, authority and inherited historical thread before any external correspondence."
---

# Correspondence Identity Gate

## Purpose

Prevent identity, beneficiary and protected-record crossover while preserving established email-thread provenance.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Recover current mission owner, beneficiary, sender policy and provider account metadata from owning mission register. Do not infer sender from an email display name or an assistant preference.
2. Check the authenticated link for the intended mailbox; stop the write if it does not match the authorized sender. A user's representative is not automatically authorized to speak, sign, consent, or receive protected records on behalf of another adult.
3. Classify communication as first-party, authorized representative, procedural routing, provider reply or internal-only. Record basis and scope of authority; do not copy protected IG, personnel, medical or court material into a less-protected case index.
4. For existing correspondence, keep original thread/account and document its routing exception. Do not forward/reapply/resubmit just to normalize an older account.
5. Return permitted provider identity, owner, channel, restricted material boundary, authorization predicate and need-for-approval status. Block ambiguous sender or consent.

## Negative and regression tests

- Reject: Wrong connected account despite correct From header
- Reject: Historic recruiter conversation in the legal mailbox
- Reject: First-party consent assumed from an agent note
- Reject: Sensitive IG-protected text copied into task description

## Output and acceptance

IDENTITY_ROUTE.json with owner, beneficiary, authenticated account, historical thread exception, authorization evidence and blocked/ready determination.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
