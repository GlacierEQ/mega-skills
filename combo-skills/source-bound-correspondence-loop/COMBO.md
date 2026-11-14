---
id: source-bound-correspondence-loop
display_name: Source-Bound Correspondence Loop
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Source-Bound Correspondence Loop

**Integration:** reuse existing APEX/Context First and the canonical long-horizon-core. Provider originals remain truth; Linear is the task projection. This is a candidate procedure, not deployed automation.

## Ordered execution and contracts

| Stage | Owning Skill | Produced contract | Failure gate |
|---|---|---|---|
| 1 | long-horizon-core | MISSION.md / CONTEXT.md / EVIDENCE.md | No fresh task starts from an unverified assumption |
| 2 | correspondence-identity-gate | IDENTITY_ROUTE.json | Correct beneficiary, owner, sender and privacy boundary or hard block |
| 3 | provider-thread-forensics | PROVIDER_TIMELINE.md / SOURCE_EVENTS.json | DRAFT and SENT are distinct; replies from beneficiary's own mailbox recovered |
| 4 | linear-frontier-deduplicator | LINEAR_RECONCILIATION.md | Action identity matched and one current owner retained |
| 5 | jurisdiction-authority-citation-check | AUTHORITY_MATRIX.md | Every legal citation has official source, scope, exceptions and verified deadline |
| 6 | adverse-outcome-remedy-router | REMEDY_BRANCHES.md | Every branch has a legitimate distinct next action; no automatic victory claims |
| 7 | precision-provider-email | EMAIL_DRAFT.md / PRE_SEND_GATE.md | False claims/duplicate send/wrong sender/privacy leaks blocked, approval before send |
| 8 | receipt-provenance-continuation | ACTION_RECEIPT.json / RESUME_CURSOR.md | Provider-native and Linear readback match or mark NEEDS_PROOF |

## Handoff and retry semantics

On any failed gate preserve source refs, correction and exact resume cursor, not a duplicate external effect. A known SENT item cannot be resent simply because recipient has not replied. Any unverified delivery or provider effect stays NEEDS_PROOF. A drafting run cannot become a sent-message claim. No email or legal filing without specific current authorization.

## Response fork

Grant: verify implementation. Partial: reconcile categories. Denial: obtain written reasons, controlling exception and lawful review route. Silence: validate rule/deadline before following up. Ambiguity: confirm delivery before retry. None of these stages guarantee victory.

## Skill maturity

All child atomic procedures are staged as candidate, not independently deployed. A runtime integration implementation and negative-path tests are needed before production-ready claims.
