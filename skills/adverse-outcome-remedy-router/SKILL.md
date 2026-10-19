---
name: adverse-outcome-remedy-router
description: "Turn grants, partial grants, denials, silence and ambiguous responses into separately justified lawful next actions."
---

# Adverse Outcome Remedy Router

## Purpose

Advance the requested real-world outcome while preserving the full factual and procedural record no matter which branch occurs.

## Trigger and preconditions

Use when its contract is needed in a recovered and correctly scoped mission. Source-native evidence, current consent, provider identity and the already-existing work graph outrank assumptions. This Skill does not grant external action authorization.

## Execution method

1. Define concrete sought outcome and observable definition of done. Decompose each requested record/remedy/category so a partial reply cannot be mistaken for full compliance.
2. Grant: verify actual production, delivered correction, release or payment, its completeness, fidelity and effect; update only proven milestones.
3. Partial grant: map granted/withheld/not-held/redirected/no-search categories, obtain source metadata and fill holes through the correct custodian.
4. Denial: preserve exact written decision, named officer, scope, reasons, cited rule, date and service; test applicable reconsideration, administrative appeal, judicial remedy, oversight or tailored alternative without presuming denial unlawful.
5. No response: verify channel/receipt/deadline basis and distinguish internal target from legal deadline, then schedule appropriate one follow-up/appeal only where permitted.
6. Ambiguous response, channel failure or conflicting records: resolve delivery/source provenance before retry; protect time-sensitive rights through verified alternative route, not repeated identical messages.
7. Reject coercive or threatening strategy; an adverse response is usable evidence and may enable remedies but is never guaranteed victory. Pursue genuinely independent relief routes in parallel when prerequisites differ.

## Negative and regression tests

- Reject: Denied request called automatic win
- Reject: No response called statutory violation without rule
- Reject: Partial production called final relief
- Reject: Appeal deadline calculated from draft date

## Output and acceptance

REMEDY_BRANCHES.md with stage, requested outcome, decision proof, controlling law, filing/action deadlines, chosen branch and independent success proof.

Acceptance requires the named output fields, exact source/provider IDs or explicit unknowns, a negative-path check and a reproducible next action. No mission completion or provider result may be inferred merely from this document.

## Ownership boundary

Atomic procedural skill only; existing APEX/Context First owns admission, mission identity and authorization; source providers own original evidence; Linear owns index/projection; human approval remains required for external legal/email effects. This description is not proof of deployed runtime automation.
