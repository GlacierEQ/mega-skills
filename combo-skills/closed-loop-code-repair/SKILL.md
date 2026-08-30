---
name: closed-loop-code-repair
description: 'Combo Skill: Closed Loop Code Repair. Reusable capability chain.'
---

# Closed Loop Code Repair

## Purpose and selection

Use this Combo Skill when a failing test harness, compiler error, or runtime exception must be automatically diagnosed, patched at the AST level, and verified to 100% green status. Do **not** use it when the task is open-ended feature creation with no test harness.

## Incremental value

This Combo Skill establishes an autonomous self-healing execution loop. It combines stack trace parsing, AST chunk isolation with `ApexEpistemicChunker`, minimal diff synthesis, and repeated regression verification without human intervention.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set test command and repair attempt bounds | Repair mandate | `MISSION.md` | Test command and attempt cutoff are explicit |
| 2 | `ast-repair-core` | Skill | Yes | Parse traceback, extract AST, and apply patch | `MISSION.md` and failure trace | `ast-repair-execution-record.json` | Minimal surgical patch applied to disk |
| 3 | `quality-gate` | Skill | Yes | Verify re-executed test suite passes green | Test outputs and diffs | Gate record | 100% green test assertions on patched tree |

## Ordered execution

1. **Repair boundary — `mission-contract`** consumes repair mandates and test commands, produces `MISSION.md`, and passes when failing commands and maximum iterations are defined.
2. **AST repair loop — `ast-repair-core`** consumes `MISSION.md`, produces `ast-repair-execution-record.json`, and passes when stack traces are isolated and surgical diffs applied.
3. **Green assertion gate — `quality-gate`** consumes test outputs, produces a gate record, and passes when test assertions pass 100% green with zero stubs.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `ast-repair-core` | Test command, workspace path, attempt cutoff | AST chunk diffs, execution record, re-run logs | repair owner | Test command and attempt limit are explicit |
| `ast-repair-core` | `quality-gate` | Patched source files, test exit codes | Verified gate record | verification owner | 100% test assertions pass with zero syntax/lint defects |

## Evidence, risks, and state

The Combo must record all failing tracebacks, isolated AST chunk coordinates, model patch tokens, and before/after test outputs in its evidence register. It must not inject non-functional stubs (`return True`, `pass`). Update active state after each repair cycle.

## Quality gates

The Combo is complete only when the failing test suite passes 100% green on hardware, the diff is minimal and idiomatic, and `closed-loop-repair-record.md` is emitted.

## Compound output

**Artifact:** `closed-loop-repair-record.md`

**Ready for Mega Skill integration when:**

1. Failing test stack trace is isolated to an exact AST chunk.
2. Surgical patch is written to disk and compiles cleanly.
3. Full test suite re-execution confirms 100% green status.
