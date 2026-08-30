---
name: apex-fleet-harmonizer
description: 'Mega Skill: apex-fleet-harmonizer. End-to-end sovereign mission system.'
---

# APEX Fleet Harmonizer Mega Skill

## Mission

Run multi-repository git branch reconciliation across large account ecosystems (e.g. GlacierEQ's 1,178 repositories) from branch discovery through synthesis, regression testing, and clutter pruning without data loss.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `recon-and-map` when repository scope or relationships are unmapped | Establishes multi-repo batch coordination and repository categorization maps. |
| `long-horizon-core` | `fleet-recon-and-harmonize` when scoped repositories have unmerged branches | Enforces regression testing gates, archive tagging, and lossless branch pruning across batches. |

## Route algorithm

1. Begin the harmonization campaign with `long-horizon-core` and initialize durable state files.
2. Partition the target account into thematic batches (e.g. Legal Tech, Aerospace, Swarm Tech).
3. Select `recon-and-map` to inspect candidate repositories and define clean branch boundaries.
4. Execute `fleet-recon-and-harmonize` for each repository in the active batch.
5. Require 100% green regression test runs before permitting code merges or branch pruning.
6. Reconcile synthesized commits, archive tags, and pruning receipts into `EVIDENCE.md` and deliver final mission report.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` remain the mission source of truth across all repository batches.
