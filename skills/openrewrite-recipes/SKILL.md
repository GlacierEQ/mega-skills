---
name: openrewrite-recipes
description: "Run OpenRewrite recipes for automated API migrations, framework upgrades, and deprecation removal. Use when a migration can be expressed as a composable, versioned, dry-runnable recipe, JVM-first."
---

# OpenRewrite Recipes

Operate OpenRewrite as the estate's recipe engine: select, compose, dry-run, and apply refactoring recipes for API migrations, framework upgrades, and deprecation removal, with the produced diff as the verification artifact.

## Workflow

1. Frame the migration: source and target API/framework versions, repositories in scope, and the acceptance tests that prove behavioral equivalence.
2. Baseline: clean working tree, build green, focused tests green; capture the baseline result before any recipe runs.
3. Select the recipe (or compose a recipe list) and pin its version; record name and version in the run plan.
4. Dry-run the recipe and review the complete diff; stop on unexpected files, generated-code edits, or semantic surprises.
5. Apply one recipe per batch; rebuild and run focused tests after each batch.
6. Run the broader suite and the repository build; repair drift with test-drift-archaeology-repair rather than weakening tests.
7. Emit the migration receipt: recipe names/versions, files considered/changed/skipped, test results, warnings, rollback (single revert of the batch commit).

## Operating the engine

OpenRewrite (source: `openrewrite/rewrite`, **Apache-2.0** — usable with attribution; verified 2026-10-21) rewrites code by running *recipes* — composable, versioned transformation units — over a lossless semantic model of the codebase.

- **Select before you run.** Find the published recipe for the migration (framework upgrade paths, deprecated-API replacements, and cleanup recipes are catalogued upstream). Prefer a maintained upstream recipe over a hand-written one; compose recipes in a declarative YAML recipe list when a migration needs several steps.
- **Dry-run first.** Run with the build plugin in dry-run mode (`rewrite:dryRun` for Maven, the Gradle plugin's dry-run task) and read the full diff before applying anything. The diff is the review artifact — an unexpected diff shape stops the run.
- **Apply in one recipe per batch.** Apply, re-run the build and the focused tests, then the broader suite. One conceptual migration per batch keeps rollback a single revert.
- **Keep the recipe.** The recipe list (name + version) goes into the migration receipt; it is the durable, re-runnable asset for the remaining repos in the estate.

## Safety gates

- Never apply a recipe whose dry-run diff has not been read end-to-end.
- Never batch two unrelated migrations into one apply; rollback granularity is one recipe.
- Keep credentials and local paths out of recipe configuration and receipts.

## Output contract

- Recipe run report with per-recipe change counts
- Migration receipt with diff, tests, and rollback path

## Related skills

- recipe-based-migration — the engine-agnostic method this skill executes on the JVM lane
- deprecation-removal — the retirement discipline that consumes these recipes
- automated-code-refactoring — bounded-batch discipline shared by all transform engines
- spiral-promotion-gate — decides whether the migrated candidate is promoted

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/openrewrite-recipes/tests -v
git diff --check
```
