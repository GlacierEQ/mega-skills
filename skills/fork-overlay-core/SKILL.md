---
name: fork-overlay-core
description: Dev Fork Doctrine automated upstream synchronization, custom overlay shielding, and regression test gatekeeping across repository forks.
---

# Fork Overlay Core

## Purpose

Automate upstream tracking across all 513 forks in `GlacierEQ`, strictly protecting decoupled overlay layers (`extensions/`, `sidecars/`, `plugins/`) while pulling upstream updates and verifying zero regression.

## Procedure

1. Fetch latest upstream commits (`git fetch upstream main`).
2. Verify that upstream tracking branch (`upstream/main`) is intact and rebaseable.
3. Isolate local modifications to protected overlay directories.
4. Merge or rebase upstream changes onto local branch without mutating overlay contracts.
5. Execute full regression test suites to guarantee 100% green status.
6. Push verified updates to `origin/main`.

## Output contract

Produce `fork-sync-audit-receipt.json` with commit ranges, overlay integrity status, test execution receipts, and remote push SHAs.

## Local validation

The procedure passes only when upstream commits are cleanly integrated, custom overlay layers remain 100% untouched, and all test suites pass with zero regressions.

## Non-goals

Do not destructively modify upstream core files. Do not push unverified or failing builds to origin.
