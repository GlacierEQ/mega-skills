---
name: provider-thread-forensics
description: "Audit provider-native email threads to distinguish drafts, sent messages, actual acknowledgments and binding decisions."
---

# Provider Thread Forensics

## Purpose

Resolve the actual position of a case before choosing another outbound action; distinguish source state from claims about source state.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Search correct account plus narrowly relevant linked accounts by stable case ID, recipient, subject, thread, notice, claim, dated rule and attachments; page results and record search cutoff/coverage.
2. Read complete source thread, message IDs, timestamps/timezones, from/to, labels, original reply-to, attachments and later replies. Separate old forwarded copies from original first-party messages.
3. Build chronological provider-events with precise stages: DRAFT, SENT, RECEIVED, ACKNOWLEDGED, ASSIGNED, PROCESSING, PRODUCED, PARTIAL, DENIED, APPEALED, REMEDIED, UNKNOWN.
4. Match receipt type to scope: SMTP Gmail SENT proves user transmission not third-party acceptance; agency acknowledgment proves receipt not merits or filing; document draft is not a filed court pleading.
5. Compare later events with earlier Linear/Notion summaries, identify which earlier instructions are stale, record any contradiction and affected work only.
6. Leave explicit unavailable/undetermined status for unsearched mailboxes, truncated threads, attachments not inspected or unverified portals. Never convert search absence into worldwide absence.

## Negative and regression tests

- Reject: Message exists as DRAFT while status says SENT
- Reject: Response in beneficiary mailbox missed by representative mailbox
- Reject: A mailed NTA is misdescribed as no hearing date
- Reject: A previous reply supersedes proposed repeat demand

## Output and acceptance

PROVIDER_TIMELINE.md and SOURCE_EVENTS.json with exact email IDs/URLs, source time, evidence stage, per-category dispositions and search scope.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
