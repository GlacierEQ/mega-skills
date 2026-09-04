---
name: branch-lifecycle-intelligence
description: "Evidence-first Git branch lifecycle intelligence for collapsing branch sprawl without destroying useful work. Inventories branches and PR lineage, proves redundancy, groups related work into synthesis families, preserves divergent value, and emits bounded cleanup plans and receipts. Use for repository branch hygiene, post-merge cleanup, stale-branch consolidation, branch-spread reduction, or reusable GitHub branch lifecycle automation."
---

# Branch Lifecycle Intelligence

## Mission

Turn branch sprawl into a compact, inspectable lifecycle without sacrificing useful work, and prevent unnecessary new refs through explicit workstream admission.

The governing rule is:

> **Prove redundancy before deletion; surface divergence for synthesis instead of treating age as proof of uselessness.**

This skill owns branch classification, cleanup confidence, family grouping, preservation decisions, and lifecycle receipts. It is intentionally stricter than a generic "delete stale branches" script.

## Dynamic Assessment Law

Every state and recommendation is provisional. The system must reassess against the latest observable state whenever new evidence arrives and immediately before any mutation.

Each branch decision carries a dynamic posture:

- `PRESERVE_AND_HARVEST` — unique or active value exists; keep it and treat it as a donor for synthesis.
- `CONSOLIDATE_AFTER_HARVEST` — likely value exists across stale/divergent work; extract and integrate useful differences before retiring anything.
- `DENY_REMOVAL` — policy, protection, recovery evidence, or active constraints make removal inappropriate.
- `REMOVE_REDUNDANT` — current evidence proves the ref contributes no unique value.
- `BLOCK_UNCERTAIN` — evidence is incomplete, contradictory, or stale; do nothing destructive.

A static classification is never authoritative by itself. Plans expire after the configured assessment TTL, and apply mode performs a fresh live reclassification before every delete.

Assess dynamically across:

- current branch SHA and topology,
- open/closed/merged PR state,
- unique commit count,
- changed-file surface,
- repository-local preservation policy,
- evidence quality and missing data,
- reversibility and rollback path,
- downstream impact and current workstream context.

## State machine

Every non-default branch must resolve to exactly one lifecycle state:

1. `PROTECTED` — default branch, protected ref, or policy-reserved long-lived branch.
2. `ACTIVE` — has an open pull request or explicit active policy signal.
3. `MERGED_REDUNDANT` — a pull request from the branch was merged; the branch ref is now lifecycle residue.
4. `REACHABLE_REDUNDANT` — branch has zero commits ahead of default; its tip contributes no unique commit.
5. `STALE_REVIEW` — inactive, old, and still divergent; requires consolidation review.
6. `DIVERGENT_PRESERVE` — contains unique commits and is not old enough for stale review.
7. `UNKNOWN_BLOCKED` — evidence is incomplete or contradictory.

Only `MERGED_REDUNDANT` and `REACHABLE_REDUNDANT` may receive automatic `DELETE` actions, and only when confidence meets policy.

## Best-of-all-worlds lifecycle

### Phase 1 — Inventory

Collect, for every branch:

- name and head SHA,
- protection status,
- head commit timestamp,
- open / merged / closed-unmerged PR lineage,
- comparison to the default branch,
- ahead / behind counts,
- changed-file sample when available,
- evidence errors.

Never infer reachability from branch names or age.

### Phase 2 — Protect

Block deletion when any of these apply:

- branch is the default branch,
- GitHub marks the ref protected,
- branch matches a configured protected pattern,
- an open PR exists,
- comparison or PR evidence is incomplete.

### Phase 3 — Prove redundancy

Prefer independent proof in this order:

1. merged PR lineage -> `MERGED_REDUNDANT`;
2. `ahead_by == 0` against default -> `REACHABLE_REDUNDANT`;
3. otherwise preserve or review.

A merged PR may have been squash-merged, so do not require the branch tip itself to be an ancestor of default before considering the branch lifecycle-complete.

### Phase 4 — Synthesize branch families

Normalize branch names into a family key by removing common actor prefixes, dates, ticket numbers, run IDs, and numeric suffixes.

Group related divergent branches. For each family:

- identify the highest-value surviving branch,
- rank active/open-PR work first,
- then unique commit count,
- then recency,
- list sibling branches as consolidation candidates,
- never auto-merge siblings solely because their names look related.

The family layer reduces branch spread by showing where multiple refs are really one stream of work.

### Phase 5 — Plan

Emit one action per branch:

- `KEEP`
- `DELETE`
- `REVIEW_CONSOLIDATE`
- `BLOCK`

Every action includes state, confidence, evidence, family, rationale, and a dynamic assessment describing value, risk, evidence quality, and the recommended effect.

### Phase 6 — Apply bounded cleanup

Apply mode may delete only when all are true:

- action is `DELETE`,
- state is `MERGED_REDUNDANT` or `REACHABLE_REDUNDANT`,
- cleanup confidence >= configured threshold,
- branch is not default/protected/reserved,
- no open PR exists at execution time,
- deletion API call succeeds against the exact ref.

Reclassify the branch from fresh GitHub state immediately before deletion. If the head, protection, PR state, or unique-commit topology changed, the previous decision expires and mutation is denied until a new assessment supports it.

### Phase 7 — Receipt

Always emit a durable receipt containing:

- repository and default branch,
- policy version,
- inventory timestamp,
- inventory SHA-256,
- plan SHA-256,
- before/after branch counts,
- classification counts,
- deleted refs,
- preserved divergent refs,
- blocked refs,
- consolidation families,
- errors and residual uncertainty.

No cleanup run is "successful" merely because branches disappeared. Success means the receipt proves what was deleted and why.

## Branch admission

Use explicit workstream identity before creating a new branch.

Admission decisions:

- `REUSE_EXISTING` — one exact live workstream binding exists; update it instead of minting another ref.
- `REVIEW_CONSOLIDATE` — multiple live branches are explicitly bound to the same workstream; stop branch creation and consolidate.
- `CREATE_NEW` — no live workstream binding exists, or an explicitly continued lifecycle is already closed.
- `CREATE_NEW_WITH_FAMILY_WARNING` — a similar branch family exists but naming alone cannot prove equivalence.
- `BLOCK` — explicit continuation points to a protected, missing, or evidence-blocked ref.

See `references/admission-protocol.md` and `resources/branch-admission.schema.json`.

## Compounded lifecycle

For repository-wide missions, route through the active Combo:

`combo-skills/branch-sprawl-control-loop/COMBO.md`

It composes:

1. `branch-lifecycle-intelligence` — inventory, classification, redundancy proof, families;
2. `pr-babysit` — protect and complete live PR work;
3. `finishing-a-development-branch` — choose integration closure;
4. `branch-lifecycle-intelligence` again — refresh evidence and clean only post-integration residue.

## Commands

```bash
python skills/branch-lifecycle-intelligence/skill.py plan snapshot.json
python skills/branch-lifecycle-intelligence/skill.py plan snapshot.json --policy resources/policy.json --output plan.json
python skills/branch-lifecycle-intelligence/skill.py validate snapshot.json
python skills/branch-lifecycle-intelligence/skill.py admit plan.json branch-admission-request.json --output admission-decision.json
```

## Reusable workflow

The repository-level workflow is:

`.github/workflows/branch-lifecycle-intelligence.yml`

Target repositories can call it from a thin wrapper using `workflow_call`. Default mode is `report`; `apply` must be explicit.

Recommended operating cadence:

- on PR close: report or apply for immediate post-merge residue,
- nightly/weekly: report across the full branch set,
- manually: apply after reviewing the generated plan for older divergent families.

## Hard invariants

- Age alone never authorizes deletion.
- Closed-unmerged is not equivalent to useless.
- Branch-name similarity is not proof of semantic equivalence.
- Divergent commits default to preservation.
- Missing comparison evidence fails closed.
- Default/protected/reserved refs are never auto-deleted.
- Apply mode must produce the same classification semantics as report mode.
- Every destructive decision expires and must be dynamically reassessed immediately before mutation.
- Static labels are observations, never permanent truth.
- New evidence may strengthen, weaken, reverse, or block a prior recommendation.
- A cleanup rule must reduce future branch production where possible, not merely sweep symptoms.

## Resources

| Resource | Purpose |
|---|---|
| `resources/policy.json` | Default protection, confidence, and staleness policy. |
| `resources/branch-inventory.schema.json` | Normalized inventory contract. |
| `resources/branch-admission.schema.json` | Explicit workstream admission request contract. |
| `references/decision-model.md` | Classification and consolidation rationale. |
| `references/admission-protocol.md` | Branch creation/reuse/consolidation decision law. |
| `templates/caller-workflow.yml` | Thin target-repository caller. |
| `scripts/branch_lifecycle.py` | Deterministic classifier and planner. |
| `tests/test_branch_lifecycle.py` | Adversarial lifecycle tests. |
