---
name: hollow-audit
description: "Audit a skill package for hollow-adapter defects: documented scripts that do not exist, presence-only tests, and capability claims with no implementation. Use when importing third-party skills, before activating any skill, or when a skill's output looks too clean."
---

# Hollow Audit

Convert a skill package into a verdict backed by execution, not by file presence. A skill is real only when its documented entrypoint runs and produces the artifact it claims.

## Activation

**Use when**
- audit this skill
- is this skill real
- check for stubs
- before importing skills
- verify skill capability

**Do not use when**
- the package has no scripts and is declared prose-only
- you only need a documentation read

## Procedure

### 1. Extract every script invocation from SKILL.md

- Evidence: list of referenced paths
- If blocked: no invocations found; record prose-only and stop

### 2. Resolve each referenced path against the skill dir and repo root

- Evidence: per-path exists/absent table
- If blocked: absent paths are the defect; list them

### 3. Check for the stub template signature

- Evidence: run.py and this_skill.py present with tiny line count
- If blocked: no stub markers; continue

### 4. Read the tests and classify each assertion

- Evidence: count of presence-only vs subprocess-backed tests
- If blocked: tests absent; note the gap

### 5. Run one documented entrypoint with a real target

- Evidence: stdout or stderr plus exit code
- If blocked: nonzero exit or missing artifact means not proven

### 6. Emit verdict with per-check evidence

- Evidence: PASS or FAIL plus the failing checks
- If blocked: report FAIL with the exact missing path

## Verification and handoff

- every documented script path resolves
- at least one entrypoint executed with observed output
- verdict states the evidence tier

Capture sources, decisions, observed outputs, unresolved risks and the exact continuation cursor.
Do not claim execution, acceptance, installation, or external provider success without provider readback.

## Behavioral evaluation

Review the six independent evaluation families in `evals/scenarios.json` with an actual host.
These are test specifications, not passing behavioral results.

## References

- [Reference 1](references/defect-classes.md)

## When not to use

- The request falls outside hollow-audit's domain; pick a closer skill.
- Only an explanation or plan is wanted, with no artifact to produce.
- A stronger activated skill covers the same ground (see scripts/strength_score.py).
