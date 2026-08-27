---
name: work-packet
description: Define a bounded, testable assignment for a specialist, agent, or sequential work chunk. Use when work must be delegated, handed off, isolated for verification, or performed without relying on implicit conversational context.
---

# Work Packet

## Purpose

Make a unit of work executable and reviewable by another actor. This Skill owns the assignment contract; it does not replace the receiving specialist’s method.

## Procedure

1. Name one concrete objective and the decision authority granted to the owner.
2. List canonical inputs, source IDs, constraints, and prior decisions the owner must use.
3. Define the expected artifact, location, format, required fields, and quality threshold.
4. Specify an acceptance test, time or scope boundary, and conditions that require escalation.
5. State prohibited actions and approval boundaries, especially for mutation, external effects, privacy, and safety.
6. Require a closing state update: evidence added, decision recorded, risk changed, and next action proposed.

## Output contract

Produce a work packet in `ROADMAP.md` or a named packet file containing objective, owner, inputs, output, validation, boundaries, escalation path, and required state update.

## Local validation

The packet passes when the owner can act without guessing critical inputs, and the integrator can accept or reject the output without asking for undocumented background.

## Non-goals

Do not assign multiple unrelated objectives, transfer private material unnecessarily, or imply authority the owner does not have.
