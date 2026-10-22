---
name: jscodeshift-codemods
description: "Author and run jscodeshift codemods for JavaScript and TypeScript API migrations. Use when an API change is expressible as a recast + Babel AST transform proven against input/output fixtures."
---

# Jscodeshift Codemods

Operate jscodeshift as the estate's JS/TS transform engine: author fixture-tested codemods, dry-run them over a target tree, and apply them in bounded, reversible batches.

## Workflow

1. Specify the migration precisely: the old AST shape, the new AST shape, and the skip rules (generated files, vendored code, fixtures).
2. Write the fixtures first, including the idempotence and skip cases; make the transform pass them.
3. Dry-run with --print over a representative sample; read every hunk.
4. Apply to the bounded target tree; run the repository's formatter, type check, and focused tests.
5. Run the broader suite; repair any drift with test-drift-archaeology-repair.
6. Emit the run receipt: transform name, files considered/changed/skipped, fixture results, suite results, rollback (revert the batch commit).

## Authoring and running transforms

jscodeshift (source: `facebook/jscodeshift`, **MIT** — usable with attribution; verified 2026-10-21) is a toolkit for writing codemods over JavaScript/TypeScript ASTs (recast + Babel).

- **Fixture-first.** Every transform ships with input/output fixture pairs (`__testfixtures__`) and a test that runs the transform over them. The fixtures are the contract: cover the plain case, the aliased import, the already-migrated file (idempotence), and the case that must be skipped.
- **Dry-run and print.** Use `--dry --print` to inspect the exact output on a sample before writing anything; use `--run-in-band` and path filters to bound the batch.
- **Idempotence is required.** Running the codemod twice must produce no second diff; a transform that is not idempotent is not finished.
- **Preserve formatting.** Recast preserves untouched code byte-for-byte; if output formatting churns unrelated lines, the transform is reaching too far — narrow the node matching.

## Safety gates

- Never run an un-fixtured transform over a real tree.
- Never use jscodeshift for purely textual renames at estate scale (route to fastmod-bulk-rewrite).
- A transform that cannot skip already-migrated code does not run twice — fix idempotence first.

## Output contract

- Codemod transform module with passing fixture tests
- Codemod run receipt with files changed/skipped and test results

## Related skills

- codemod-cli — lifecycle manager for scaffolded, shared, multi-step codemods
- automated-code-refactoring — bounded-batch discipline shared by all transform engines
- recipe-based-migration — the method pattern this engine implements for JS/TS

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/jscodeshift-codemods/tests -v
git diff --check
```
