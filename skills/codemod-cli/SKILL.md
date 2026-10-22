---
name: codemod-cli
description: "Manage the codemod lifecycle with the codemod CLI: scaffold, share, dry-run, and execute multi-step codemods of any size, with first-class ast-grep and jscodeshift support."
---

# Codemod CLI

Operate the codemod CLI as the estate's codemod lifecycle manager: scaffold new codemods, publish and reuse shared ones, and run multi-step migrations with dry-run reports before any write.

## Workflow

1. Specify the migration and choose the engine per step (ast-grep for syntactic patterns, jscodeshift for semantic JS/TS transforms).
2. Scaffold the codemod package; write its tests/fixtures before its transforms.
3. Dry-run against the first target repository; review the report end-to-end.
4. Apply in bounded batches; run repository tests after each batch.
5. Publish the proven package to the estate's shared set with its receipt; reuse for subsequent repositories.
6. Emit the lifecycle receipt: package name/version, steps, reports, test results, rollback per step.

## The lifecycle

The codemod CLI (source: `codemod/codemod`, **Apache-2.0** — usable with attribution; verified 2026-10-21) scaffolds, shares, and runs codemods — from a single ast-grep pattern to multi-step migrations mixing engines.

- **Scaffold, don't improvise.** New codemods start from the CLI scaffold so structure, tests, and metadata are uniform across the estate.
- **Dry-run is the default.** Every run produces a report before writes; the report is reviewed like a diff.
- **Multi-step stays ordered.** When a migration needs several codemods in sequence, declare the order in the package; each step is independently dry-runnable and reversible.
- **Share deliberately.** A codemod proven on one repo is published inside the estate before it is run on the next; estate-wide runs reuse the tested package, not a copy.

## Safety gates

- Never run a codemod package that has not passed its own fixture tests.
- Never skip the dry-run report on a new target repository, even for a proven package — targets differ.
- Keep per-step rollback independent; a failed step never leaves earlier steps unrecorded.

## Output contract

- Scaffolded codemod package with tests
- Codemod run report (dry-run and applied) with receipts

## Related skills

- jscodeshift-codemods — the JS/TS transform engine this CLI orchestrates
- ast-grep-structural-rewrite — the pattern engine this CLI orchestrates
- recipe-based-migration — the method pattern for versioned, composable migrations

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/codemod-cli/tests -v
git diff --check
```
