---
name: upstream-fork-harmonization
description: 'Combo Skill: Upstream Fork Harmonization. Reusable capability chain.'
---

# Upstream Fork Harmonization

## Purpose and selection

Use this Combo Skill when repository forks must be synchronized with their upstream source codebases while strictly protecting local overlay layers (`extensions/`, `sidecars/`, `plugins/`). Do **not** use it when the repository is an upstream canonical master.

## Incremental value

This Combo Skill enforces the Dev Fork Doctrine across distributed forks. It adds clean upstream tracking, overlay shielding, conflict isolation, and regression test gatekeeping that prevents destructive drift.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set fork scope and overlay protection criteria | Sync mandate | `MISSION.md` | Fork repo and protected layers are explicit |
| 2 | `fork-overlay-core` | Skill | Yes | Pull upstream main, protect overlays, merge cleanly | `MISSION.md` and repository | `fork-sync-audit-receipt.json` | Upstream commits merged; overlays untouched |
| 3 | `quality-gate` | Skill | Yes | Verify regression suites before origin push | Test results and diffs | Gate record | 100% green test assertions on merged tree |

## Ordered execution

1. **Fork boundary — `mission-contract`** consumes sync mandates and fork repository paths, produces `MISSION.md`, and passes when upstream remote URLs and protected overlay directories are defined.
2. **Overlay sync — `fork-overlay-core`** consumes `MISSION.md`, produces `fork-sync-audit-receipt.json`, and passes when upstream commits are fetched and merged with overlays intact.
3. **Regression gate — `quality-gate`** consumes test logs and git diffs, produces a gate record, and passes when local regression suites pass 100% green before push.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `fork-overlay-core` | Fork repository path, upstream remote, overlay paths | Cleanly merged working tree and audit receipt | fork owner | Upstream remote and protected directories are explicit |
| `fork-overlay-core` | `quality-gate` | Merged tree, test suite command, audit receipt | Verified gate record | verification owner | 100% tests pass green with zero overlay modifications |

## Evidence, risks, and state

The Combo must record all upstream commit ranges, merge conflict resolutions, overlay hash digests, and test logs in its evidence register. It must not destructively modify upstream core files. Update active state after each fork synchronization.

## Quality gates

The Combo is complete only when upstream commits are integrated without conflict, overlay directories match pre-merge hashes, regression tests pass 100% green, and `upstream-fork-record.md` is emitted.

## Compound output

**Artifact:** `upstream-fork-record.md`

**Ready for Mega Skill integration when:**

1. Upstream commits are fetched and merged into local tracking branch.
2. Protected overlay directories remain cryptographically unmodified.
3. Local regression suites pass with zero regressions.
