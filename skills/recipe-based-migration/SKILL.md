---
name: recipe-based-migration
description: "Express an API or framework migration as a composable, versioned, dry-runnable recipe: run it estate-wide, review the diff as the verification artifact, and keep the recipe as the durable migration asset. The OpenRewrite method, engine-agnostic."
---

# Recipe Based Migration

Own the recipe method independent of any one engine: a migration is not a one-off edit but a named, versioned, composable recipe whose dry-run diff is reviewed before application and whose identity is recorded in every receipt.

## Workflow

1. Specify the migration as from-state → to-state; decompose into the smallest composable recipe steps.
2. Implement the recipe on the chosen engine; name and version it; add its fixture/dry-run tests.
3. Dry-run on the first target; review the diff; fix the recipe (version bump) rather than hand-editing output.
4. Apply per repository in bounded batches; each application emits a receipt citing recipe name, version, and SHA.
5. Track estate coverage from receipts: applied, pending, exempted (with reason) — the migration is done when the coverage table is complete.
6. Archive the recipe with the migration record; it is the re-runnable asset for stragglers and audits.

## The method

**Provenance:** method lineage — the OpenRewrite project (docs, Apache-2.0) generalized across engines. Registered as an estate method with attribution; it prescribes *how migrations are expressed*, whichever engine runs them.

Four commitments distinguish a recipe migration from a find-and-replace campaign:

1. **Named and versioned.** The migration is an artifact with an identity (`framework-x-2-to-3`, v1.2) — not a script run once and lost. Fixes to the migration bump the recipe, not a fork of it.
2. **Composable.** Large migrations decompose into small recipes that compose (rename → restructure → rewire), each independently dry-runnable, so a failure localizes to one step.
3. **Dry-run diff is the review.** No recipe applies anywhere without a reviewed dry-run diff on that target. The diff, not the recipe author's confidence, is the verification artifact.
4. **Receipts cite the recipe.** Every application records recipe name + version + target SHA, making the estate's migration state queryable: which repos ran which recipe version is a fact, not a memory.

## Safety gates

- Never hand-edit a recipe's output to fix a bad transform — fix the recipe and re-run, or the next repo gets the bug.
- Never apply without a target-specific dry-run; a recipe proven on one repo is unproven on the next.
- Exemptions are recorded with reasons in the coverage table; silent skips make coverage claims false.

## Output contract

- Named, versioned recipe definition (declarative or transform code) with dry-run evidence
- Per-repo application receipts referencing the recipe identity

## Related skills

- openrewrite-recipes — the JVM engine where this method originates
- codemod-cli — lifecycle tooling for recipe-style codemod packages
- jscodeshift-codemods — the JS/TS engine for recipe-expressed migrations
- automated-code-refactoring — bounded-batch discipline recipes execute under

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/recipe-based-migration/tests -v
git diff --check
```
