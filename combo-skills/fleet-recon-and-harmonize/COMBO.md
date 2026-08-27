---
id: fleet-recon-and-harmonize
display_name: Fleet Recon and Harmonize
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Fleet Recon and Harmonize

## Purpose and selection

Use this Combo Skill when unmerged git branch clutter across one or more repositories must be audited, synthesized into `main`, tested, and safely pruned without data loss. Do **not** use it when the task is a simple local git commit or single-file edit; route to standard git workflows instead.

## Incremental value

This Combo Skill turns raw git history divergence into an evidence-backed synthesis and cleanup plan. It adds branch divergence calculation, regression test gating, and cryptographic archive tagging that no individual member owns.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set harmonization scope and safety gates | Target repo scope | `MISSION.md` | Non-destructive boundaries are explicit |
| 2 | `fleet-git-harmonizer-core` | Skill | Yes | Audit divergence, synthesize, tag, and prune | `MISSION.md` and repository path | `fleet-harmonization-record.md` | Zero data loss verified via archive tags |
| 3 | `quality-gate` | Skill | Yes | Verify regression suites and pruning receipts | Synthesis record and test results | Gate record | 100% green tests before branch deletion |

## Ordered execution

1. **Mission boundary — `mission-contract`** consumes candidate repository scopes, produces `MISSION.md`, and passes when safety boundaries and test commands are explicit.
2. **Divergence and synthesis — `fleet-git-harmonizer-core`** consumes `MISSION.md`, produces `fleet-divergence-audit.json` and synthesized branches, and passes when commits are merged and archive tags applied.
3. **Regression gate — `quality-gate`** consumes test outputs and synthesis logs, produces a gate record, and passes when test assertions pass 100% green.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `fleet-git-harmonizer-core` | Repository scopes, branch retention rules | Verified divergence manifest and synthesis diffs | mission owner | Scope and safety gates are explicit |
| `fleet-git-harmonizer-core` | `quality-gate` | Synthesized tree, test results, archive tags | Verified gate record | execution owner | Tests green and archive tags cryptographically verified |

## Evidence, risks, and state

The Combo must record all commit SHAs, divergence counts, archive tag names, and test outputs in its evidence register. It must not force-push to remote branches or delete unarchived branches. Update active state after each repository batch completes.

## Quality gates

The Combo is complete only when all candidate branches are either synthesized into `main` or safely archived, regression tests pass 100% green on `main`, and `fleet-harmonization-record.md` is emitted.

## Compound output

**Artifact:** `fleet-harmonization-record.md`

**Ready for Mega Skill integration when:**

1. Every pruned branch has a verified archive tag.
2. Regression test suites pass with zero regressions.
3. Unmerged commits and provenance trailers are documented.
