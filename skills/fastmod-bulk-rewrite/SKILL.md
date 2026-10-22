---
name: fastmod-bulk-rewrite
description: "Fast multi-threaded partial-code rewrites with fastmod for estate-wide mechanical renames and patterned replacements where regex-with-guardrails is sufficient and AST tooling is unnecessary."
---

# Fastmod Bulk Rewrite

Operate fastmod as the estate's bulk mechanical rewrite tool: run guarded regex replacements across many files and repositories at speed, with extensions filters, accept/review flow, and post-run verification.

## Workflow

1. Write the pattern and replacement; record why regex is safe for this exact token/shape.
2. Run against one repository with review flow; audit matches and the resulting diff sample.
3. Apply per repository in sequence; run each repository's focused tests before moving on.
4. Spot-check diffs in every repository (fixed sample size); stop the estate run on the first surprise.
5. Emit the bulk rewrite receipt: pattern, replacement, per-repo counts, samples checked, test results, rollback per repo.

## Guardrails for regex at scale

fastmod (source: `facebookincubator/fastmod`, **Apache-2.0** — usable with attribution; verified 2026-10-21) is a fast, multi-threaded partial-code rewrite tool — essentially codemod-style regex replacement with review/accept flow and extension filtering.

- **Justify the regex.** fastmod is legitimate exactly when the pattern cannot appear in a misleading context: unique identifiers, literal tokens, comment-free zones proven by sampling. Write the justification into the run plan; if you cannot, use a structural engine.
- **Extensions and roots are the scope.** Filter hard by extension and directory; estate-wide means many bounded runs, not one unbounded run.
- **Sample before and after.** Read a random sample of matches before applying and a sample of diffs after; bulk speed is no excuse for unexamined output.

## Safety gates

- Never run fastmod where the pattern can occur inside strings, comments, or generated code that must not change.
- Never let one estate-wide invocation cross repositories without per-repo test gates.
- A failed spot-check halts the whole run; speed never outranks the sample.

## Output contract

- fastmod run report (changed/unchanged files)
- Bulk rewrite receipt with counts, spot-check evidence, and test results

## Related skills

- comby-structural-replace — structural replacement one rung above regex
- ast-grep-structural-rewrite — the AST-precise engine
- automated-code-refactoring — bounded-batch discipline shared by all transform engines

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/fastmod-bulk-rewrite/tests -v
git diff --check
```
