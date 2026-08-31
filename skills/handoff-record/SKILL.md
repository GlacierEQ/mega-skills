---
name: handoff-record
description: "Preserve an exact, safe recovery point for unfinished or transferred work. Use before interruption, delegation, compaction, environment changes, phase transitions, or any mission that must resume without re-discovering its critical state."
---


# Handoff Record

## Purpose

Allow a future operator to resume a mission accurately. This Skill owns recovery fidelity, not the work itself.

## Procedure

1. State the current phase, completed chunks, validated artifacts, and unresolved blockers.
2. Record the exact next action, its owner, required inputs, and the acceptance test that closes it.
3. Link the mission, roadmap, context capsule, evidence register, and any relevant work packet.
4. Capture environment facts, current revision, access limits, approvals, and external dependencies that must be rechecked.
5. Separate observed facts from assumptions and state the next review trigger for each active assumption.
6. Note failed approaches, why they failed, and the safe alternative route; never leave an unexplained dead end.

## Output contract

Produce `HANDOFF.md` with resume point, verified progress, environment facts, blockers, exact next action, and recovery checks.

## Local validation

The handoff passes when an uninvolved operator can verify the environment, load only the named state, perform the next action, and understand what must not be repeated.

## Non-goals

Do not close a handoff with vague statements such as “continue later” or conceal failed attempts that could be repeated unsafely.
