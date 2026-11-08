---
name: quality-gate
description: "Verify that a phase, artifact, or mission outcome satisfies its stated contract before work advances. Use at phase boundaries, before irreversible actions, after specialist handoffs, and before final delivery."
---


# Quality Gate

## Purpose

Turn “done” into an evidence-backed decision. This Skill owns objective phase acceptance, including explicit exceptions; it does not create the underlying deliverable.

## Procedure

1. Read the acceptance criteria, artifact contract, evidence register, and relevant risk boundaries.
2. Inspect the artifact or execute the promised test. Do not rely on a creator’s unverified claim.
3. Check completeness, correctness, consistency, traceability, usability, and applicable safety or policy constraints.
4. Seek an independent verifier when creator bias or material consequence affects confidence.
5. Record pass, fail, or conditional pass. A conditional pass must name the exception owner, expiry, impact, and review trigger.
6. On failure, classify the cause, return it to the correct owner, and prohibit advancement until the route is revised or approval is recorded.

## Output contract

Produce a gate record in `EVIDENCE.md` or `ROADMAP.md` containing criterion-to-evidence mappings, test result, decision, exceptions, owner, and next action.

## Local validation

The gate passes when a non-creator can reproduce the decision from named criteria and evidence, and a failed gate leaves an actionable remediation route.

## Non-goals

Do not treat effort, elapsed time, or visual plausibility as a quality result.
