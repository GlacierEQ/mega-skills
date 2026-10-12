---
name: progressive-pyramid
description: "Use for substantive missions requiring research, engineering, case development, integration, deployment, or progressively improved deliverables. Four Corners (Context, Objective, Constraints, Resources) plus Center Point: every corner inherits the previous version's working result, no corner starts from zero, and only the Center Point may declare MISSION_COMPLETE."
---

# Progressive Pyramid Protocol

Four Corners + Center Point. One inherited working result, advanced toward the
original mission finish line. Different agents may specialize (research,
engineering, law, memory, deployment) while following the same method of
accumulating work toward a verified finish line.

Machine-readable contract: progressive_pyramid.contract.json
Certification suite: certification.md
Worked examples: examples/

## Governing principle

Every corner must advance ONE inherited working result toward the ORIGINAL
mission finish line.

    Recover before recreating.
    Compound before replacing.
    Execute before declaring completion.

## Mission initialization

Recover existing context, prior verified gains, original operator intent, and
relevant source truth. Define:

- Original mission ID and intended outcome
- Externally observable acceptance criteria
- Protected existing capabilities
- Authoritative sources and evidence
- Current execution and continuation state

Do not substitute intermediate milestones for success.

## Corner 1 — CONTEXT -> V1

Recover prior work and source evidence.
Create the first substantive working result.
Record provenance and unresolved uncertainty.

## Corner 2 — OBJECTIVE -> V2

Inherit V1 without discarding verified gains.
Strengthen the result against the actual finish line.
Address missing objectives and dependencies.

## Corner 3 — CONSTRAINTS -> V3

Inherit V2.
Adversarially inspect errors, regressions, hidden harms, contradictions,
safety, legality, and requirements.
Correct defects without weakening prior capabilities.

## Corner 4 — RESOURCES -> V4

Inherit V3.
Use available agents, tools, connectors, sources, code, and authorized
execution surfaces.
Advance the actual deliverable and operational outcome.

## CENTER POINT

Integrate the accumulated result.
Reconcile conflicts among corners.
Execute outstanding requirements.
Independently verify real-world effects.

If processing is complete but the outcome is not:
- Preserve the result.
- Select the next unlocked action.
- Continue the mission.

If external dependencies block execution:
- Preserve the blocker and alternate routes.
- Do not claim mission completion.

Only declare MISSION_COMPLETE when the original acceptance conditions are
demonstrably satisfied.

## Recursion

Any corner may invoke this same protocol for a subordinate problem.
Subordinate completion must return its validated results to the parent mission.

## Memory and continuity

Read scoped authoritative memory before acting.
Persist verified corrections at the owning source.
Preserve evidence provenance and version history.
Never copy private case facts into unrelated scopes.

## Required execution proof

- Protocol version and mission identity
- Inherited result lineage (V1 -> V2 -> V3 -> V4)
- Material improvements across corners
- Actual actions performed
- Validation and source-native receipts
- Remaining work or verified terminal outcome


## Executable handoff and completion gate

This Skill is registered as an Atomic Skill because the inherited-result
validation is reusable inside multiple Compound and Mega missions. The
pyramid of work can still be mission-scale; scale does not duplicate the
contract or entitle any agent to call an intermediate pass MISSION_COMPLETE.

The host may validate an active/blocked run receipt with:

    python3 skills/progressive-pyramid/scripts/validate_run.py RUN.json

The CLI deliberately rejects MISSION_COMPLETE: only a trusted host that
injects an independent provider-aware `verifier(criterion, receipt_ref)`
into `validate_run(..., verifier=...)` can verify the terminal condition.
A JSON flag claiming verification is not proof.

Run local behavior tests:

    python3 -m unittest discover -s skills/progressive-pyramid/tests -v

This validator checks stage order, inherited artifact references, preserved
verified-gain IDs, mission context, blocked continuation, and outcome-proof
coverage. It does not by itself certify agent startup loading, discoverability
in every host, external evidence authenticity, or live cross-agent handoff.
These remain required before claiming multi-host certification.
