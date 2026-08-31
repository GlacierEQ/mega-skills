---
name: mission-contract
description: "Convert a request into a bounded, testable mission contract. Use when work has material scope, dependencies, risk, approvals, multiple deliverables, or ambiguity that must be resolved before execution."
---


# Mission Contract

## Purpose

Translate an incoming request into a durable contract before expensive, irreversible, or multi-step work begins. This Skill owns mission framing only; it does not select a technical implementation or perform the work.

## Procedure

1. State the requested outcome in one observable sentence.
2. Separate included deliverables from explicit exclusions.
3. Identify stakeholders, constraints, dependencies, approvals, privacy boundaries, and irreversible actions.
4. Define acceptance criteria that can be checked from artifacts, tests, sources, or approval records.
5. List material unknowns. Resolve a blocking unknown before acting; otherwise record a bounded assumption with a review trigger.
6. Define the stop condition and the next decision required to begin execution.

## Output contract

Produce `MISSION.md` with the outcome, scope, exclusions, constraints, acceptance criteria, assumptions, approvals, risks, and stop condition. Write only conclusions that a future operator needs; link detailed evidence rather than copying it.

## Local validation

The contract passes only when an independent reviewer can identify what success means, what must not be done, what evidence proves completion, and what approval is still required without reopening the raw conversation.

## Non-goals

Do not manufacture certainty, treat a broad aspiration as acceptance criteria, or authorize an external effect that the user has not approved.
