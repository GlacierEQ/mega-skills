---
name: ast-grep-structural-rewrite
description: "Structural search, lint, and rewrite by AST pattern with ast-grep. Use as the default structural transform engine for Python, TypeScript, and Rust repos when the change is syntactic structure, not text."
---

# Ast Grep Structural Rewrite

Operate ast-grep as the estate's default structural engine: write AST patterns and YAML rules to search, lint, and rewrite code by syntax tree shape across many languages, with dry-run diff review before applying.

## Workflow

1. Draw the match and replacement as example code; confirm the change is purely structural.
2. Write the pattern/rule; run in search mode and audit the full match list for false positives and missed variants.
3. Add rule tests (valid/invalid snapshots) covering the variants found.
4. Dry-run the rewrite; read the complete diff.
5. Apply in bounded batches; run formatters and focused tests, then the broader suite.
6. Re-run the search: zero remaining matches is the completeness proof. Emit the rewrite receipt.

## Patterns and rules

ast-grep (source: `ast-grep/ast-grep`, **MIT** — usable with attribution; verified 2026-10-21) matches and rewrites code by AST pattern: you write example code with metavariables (`$VAR`, `$$$ARGS`) and it finds every structurally matching site.

- **Write the pattern as code.** A pattern is an example of the shape, not a regex; if the change cannot be drawn as an example, ast-grep is the wrong engine.
- **Rules as YAML.** Package searches/rewrites as rule files with `id`, `language`, `pattern`/`fix`, and severity — rules are reviewable, testable (rule test snapshots), and reusable as lint gates after the migration.
- **Interactive review for first runs.** Use interactive/dry-run mode on the first target; automated apply only after the match set is proven to contain no false positives.
- **Keep the rule.** A migration rule that still matches after the rewrite proves completeness; a rule kept as lint prevents regression.

## Safety gates

- Never apply a rewrite whose search results were not audited — structural patterns over-match silently.
- Never express semantic conditions (types, imports resolution) as ast-grep patterns; use a semantic engine.
- Keep excluded paths (generated, vendored, fixtures) explicit in every rule invocation.

## Output contract

- ast-grep rule set (YAML) with match/rewrite evidence
- Rewrite receipt with files matched/changed/skipped and test results

## Related skills

- comby-structural-replace — lighter structural replacement when full AST tooling is overkill
- codemod-cli — lifecycle manager that can package ast-grep rules into shared codemods
- automated-code-refactoring — bounded-batch discipline shared by all transform engines

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/ast-grep-structural-rewrite/tests -v
git diff --check
```
