---
name: fleet-git-harmonizer-core
description: "Autonomous git history analysis, branch divergence reconciliation, and clutter pruning across repositories."
---


# Fleet Git Harmonizer Core

## Purpose

Audit branch divergence across git repositories, synthesize non-conflicting commits into `main`, generate sovereign Monolith archive tags, and prune branch clutter while verifying regression suites.

## Procedure

1. Fetch and prune all remote references (`git fetch --all --prune`).
2. Enumerate unmerged branches and compute commit divergence against `origin/main`.
3. Extract semantic AST diffs of unique commits on unmerged branches.
4. Synthesize non-conflicting commits into `main` with detailed commit provenance trailers.
5. Execute regression test suites before permitting any merge to stand.
6. Apply immutable archive tags (`archive/{category}/{subcategory}/{repo}/{branch}_{timestamp}`) before deleting any branch.
7. Delete merged or archived branches locally and remotely.

## Output contract

Produce `fleet-divergence-audit.json` containing repository scopes, divergence counts, synthesized commit SHAs, archive tag names, and test execution receipts.

## Local validation

The procedure passes only when zero data loss is cryptographically verified via archive tags, regression test suites pass 100% green before push, and dead branches are pruned.

## Non-goals

Do not delete branches without archive tags. Do not push failing code. Do not force-push to protected branches.
