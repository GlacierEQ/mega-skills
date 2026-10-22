---
name: comby-structural-replace
description: "Lightweight structural search-and-replace with Comby for nearly any language. Use when a full AST codemod is overkill but a plain regex would be unsafe against strings, comments, and nesting."
---

# Comby Structural Replace

Operate Comby as the estate's lightweight structural replacement tool: match code with hole-based templates that respect balanced delimiters, review matches, and rewrite in bounded batches.

## Workflow

1. Write the match and rewrite templates; name holes by the role they play.
2. Run in review mode over the bounded target; accept/reject matches until the match set is exactly right.
3. Apply the accepted replacement set as one batch; run formatters and focused tests.
4. Re-run the match template: zero matches (outside explicit skips) is the completeness proof.
5. Emit the replacement receipt: templates, files matched/changed/skipped, test results, rollback.

## Templates with holes

Comby (source: `comby-tools/comby`, **Apache-2.0** — usable with attribution; verified 2026-10-21) performs structural search-and-replace: templates use typed holes (`:[name]`, `:[name.]`, `:[name\n]`) that match balanced, nested code — unlike regex, a hole will not stop mid-expression or leak into strings and comments by default.

- **Review mode first.** Comby's interactive review shows each match in context; the first run on any tree is review-only.
- **Scope by extension.** Comby is language-generic; constrain by file extension and path so templates only meet the syntax they were written for.
- **Know the ceiling.** Comby understands delimiters, not grammars or types. When a rewrite depends on what a symbol *is*, graduate to ast-grep or a semantic engine.

## Safety gates

- Never run Comby in blind apply mode on a tree it has not reviewed.
- Never stretch a template past delimiter-level structure; graduate engines instead.
- Keep the template pair in the receipt — it is the auditable definition of the change.

## Output contract

- Comby review report of all matches
- Replacement receipt with counts and test results

## Related skills

- ast-grep-structural-rewrite — the grammar-precise structural engine
- fastmod-bulk-rewrite — the regex-with-guardrails bulk tool
- automated-code-refactoring — bounded-batch discipline shared by all transform engines

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/comby-structural-replace/tests -v
git diff --check
```
