---
name: hidden-harm-github
description: "Counter-engineer hidden harms in GitHub/repository work: prevent branch/donor capability loss, stale-CI authority, destructive simplification, false merge/completion claims, and provenance loss while preserving stronger code and optionality."
---

# Hidden Harm — GitHub

## Mission

Remove hidden harm from repository, branch, PR, CI, release, and deployment decisions. A GitHub action may be technically valid and still make the estate weaker by dropping unique capability, collapsing lineage, treating stale CI as current truth, or converting a support artifact into the mission.

## Protected dimensions

- unique branch/donor capability
- repository and commit provenance
- stronger current behavior
- reversible integration path
- deployment/source correspondence
- test and CI evidentiary scope
- unresolved dependencies and optionality
- Operator-defined architecture and intended outcome

## Hidden harms to detect

1. **Branch-status substitution:** age, behind-count, closure, divergence, or no-common-ancestor is treated as proof of irrelevance.
2. **Wholesale replacement:** a donor with one useful mechanism replaces a stronger living implementation.
3. **Stale-failure gravity:** an old failing workflow/deployment is treated as evidence current source is broken.
4. **PR-completion inflation:** opened/mergeable/reviewed is treated as merged; merged is treated as deployed; deployed is treated as healthy.
5. **CI authority inflation:** infrastructure/tooling failure becomes a code verdict without independent proof.
6. **Provenance destruction:** force-push/delete/archive/flatten removes the ability to reconstruct where capability came from.
7. **Support-work capture:** branch cleanup, receipts, governance, or CI bookkeeping displaces the actual product/case/job objective.
8. **Diff blindness:** a merge/cherry-pick is accepted without verifying the exact beneficial delta and preserved behavior.

## Execution

`RECOVER COMPLETE RELEVANT BRANCH/DONOR GRAPH -> INSPECT SOURCE -> DIFF UNIQUE CONTRIBUTIONS -> TEST CURRENT VS DONOR MECHANISM -> SELECT LOSSLESS INTEGRATION -> MUTATE -> READ BACK -> TEST -> VERIFY DOWNSTREAM EFFECT -> PRESERVE LINEAGE`

Before retirement, prove zero unique beneficial contribution and read back the merged target. Before source repair from a failed deployment, compare the failed commit to current source. Before merge, identify what gets added, what could be lost, and rollback.

## Harm states

- `BLOCKED_HIDDEN_HARM_BRANCH_LOSS`
- `BLOCKED_HIDDEN_HARM_WHOLESALE_REPLACEMENT`
- `STALE_FAILURE_DO_NOT_REPAIR_CURRENT_SOURCE`
- `CI_SCOPE_INSUFFICIENT_FOR_CODE_VERDICT`
- `MERGE_STATE_NOT_DEPLOY_STATE`
- `PROVENANCE_PRESERVATION_REQUIRED`

## Success

Success is not a cleaner branch graph. Success is a stronger living implementation with unique beneficial mechanisms preserved, exact source lineage retained, and the claimed integration/deployment state independently read back.
