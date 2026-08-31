---
name: mega-skills-test-runner
description: "Run and diagnose the local hierarchy validator and full regression suite for a GlacierEQ Mega Skills repository checkout. Use before committing registry, Skill, Combo Skill, Mega Skill, schema, validator, or governance changes."
---


# Mega Skills Test Runner

## Purpose

Run the canonical local quality gate for a **trusted** Mega Skills checkout. The gate verifies the Skills → Combo Skills → Mega Skills graph, executes all repository regression tests, detects whitespace errors in the pending diff, and can emit a JSON evidence record. It is a validation tool, not a deployment or mutation tool.

## Before running

Confirm that the repository is trusted and that its current revision is the intended target. The runner invokes the repository’s validator and test code; do not point it at untrusted code. Read `references/checks.md` if a failure needs diagnosis or the repository layout differs from the standard tree.

## Standard workflow

1. From the repository root, inspect `git status --short --branch` so results are tied to a known revision and working state.
2. Run the bundled script:

   ```bash
   python /path/to/mega-skills-test-runner/scripts/run_checks.py --repo .
   ```

3. For release evidence, write a report outside the repository’s tracked source tree unless the repository explicitly governs validation receipts:

   ```bash
   python /path/to/mega-skills-test-runner/scripts/run_checks.py \
     --repo . \
     --report /tmp/mega-skills-validation.json
   ```

4. If every check passes, record the revision and report path in the change evidence. If any check fails, stop the release, preserve the output, diagnose the first failure, and rerun the full suite after the fix.

## What the runner checks

| Check | Command | Fails when |
|---|---|---|
| Hierarchy graph | `python3 scripts/validate_hierarchy.py` | Registry, entrypoint, dependency, Combo contract, or Mega route control is invalid. |
| Regression suite | `python3 -m unittest discover -s tests -v` | Any hierarchy rule no longer matches expected behavior. |
| Diff hygiene | `git diff --check` | The working diff has whitespace errors. |
| State capture | `git status --short --branch` | Never a pass/fail check; recorded to identify the tested revision state. |

## Failure handling

Do not patch around a failing assertion without establishing whether the contract, registry, or test is wrong. Follow the failure from validator message to the named entry or field. If a test exercises an intended behavior change, update the implementation and test together, then add or revise a focused regression test so the reason for the change remains explicit.

## Non-goals

Do not use this Skill to auto-fix failures, modify a Git repository, push a branch, change external configuration, or certify that unexecuted capability procedures are valid. A passing repository graph proves contract consistency, not domain correctness or runtime readiness.

## Resources

| Resource | Use |
|---|---|
| `scripts/run_checks.py` | Execute the canonical local validation sequence and optionally emit JSON evidence. |
| `references/checks.md` | Interpret checks, expected repository layout, and common failure boundaries. |
