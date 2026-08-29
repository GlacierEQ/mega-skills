# 00 — Shared Rituals

Every recipe uses three rituals. Keep this file lean — recipes reference it
instead of duplicating.

## What's in each recipe (one-line summary)

| Recipe | Key step | Universal DoD additions |
|--------|----------|-------------------------|
| `01-add-a-feature` | Test first, then implement minimum to pass | Feature registered in the project's manifest (allowlist, identity, etc.) |
| `02-fix-a-bug` | Reproduce with a failing test, fix at the root cause | The failing test now passes; no `try/except: pass` patterns in the diff |
| `03-refactor` | One mechanical change per commit; run tests after each | All tests that passed before still pass (behavior preserved) |
| `04-review-a-pr` | Walk the diff by risk (correctness → tests → security → style → scope) | Verdict is one of: Approve, Comment, Request changes, Reject |
| `05-debug-a-test-failure` | Read failure → read test → read code (in that order) | For flaky tests, prove it by running 10× |

## Pre-Flight (Always)

Before touching a single line of code:

1. **Locate the project.** `pwd` and read the project's `AGENTS.md` (if any).
   Confirm you're in the right repo, branch, and project root.
2. **Read the file you're about to change.** Even if you wrote it yesterday.
   Per `clean-code`: "Read before write."
3. **Find dependents.** Three greps, in this order:
   - Who imports this file?  → `grep -rn "from <module> import\|import <module>" <project>`
   - What does this file import? → read the imports section
   - What tests cover this file? → `grep -rn "<ClassName>\|<function_name>" <project>/tests`
4. **State the change in one sentence.** "This change does X by modifying Y
   so that Z." If you can't, you're not ready to edit.
5. **State the test plan.** "After the change, the following tests must pass:
   A, B, C." If you can't, write the test first.
6. **Check for secrets.** Anything you might write must not contain keys,
   tokens, JWTs, or private keys. The vault is `/root/.vault_env`. Do not
   import it; do not inline it.

If any step is unclear or impossible, **stop and ask the user**.

## In-Flight (Always)

While making changes:

1. **Edit the file + all dependents together.** See "Single Most-Important
   Rule" in `SKILL.md`.
2. **No drive-by changes.** If you notice something else that needs fixing
   while you're in the file, note it; don't fix it in this commit.
3. **Match existing style.** Indentation (tabs vs spaces), naming, imports
   order. Don't impose a new style; follow the file.
4. **Comments only when naming can't carry the meaning.** Per `clean-code`:
   "If you need a comment to explain a name, rename it." Code > comments.
5. **Small functions, deep modules.** Per `clean-code`: "Max 20 lines,
   ideally 5–10." If a function grows, split it.
6. **Guard clauses over nesting.** Per `clean-code`. Early return on
   edge cases. Max 2 levels of indentation.

## Post-Flight (Always)

After the change is made:

1. **Re-read your diff.** `git diff <file>` (or equivalent). Look for:
   - Imports you forgot
   - Comments that lie (they will, after edits)
   - Dead code you didn't mean to leave
   - Debug prints
2. **Run the project's test command.** See the table in `SKILL.md` for the
   canonical command per project. If tests fail, do not declare done.
3. **Run the project's lint/typecheck if it has one.** Only the commands
   the project documents. If none exist, skip with a note.
4. **Verify dependents still resolve.** Either by running their tests or
   by import: `python -c "from <module> import <name>"` from the project root.
5. **Self-review against the task type's recipe checklist.** Each recipe in
   `0X-*.md` has a "Definition of Done" section. Walk it.
6. **State what you did and what you verified.** One short paragraph.
   "Changed `X` to do Y. Verified: tests A, B, C pass; lint clean;
   dependents D, E still import correctly."

If any post-flight step fails, return to in-flight. Do not declare done.

## Universal Anti-Patterns (Banned In All Recipes)

| Anti-pattern | Why banned |
|---|---|
| Comment every line | Per `clean-code`. Code self-documents. |
| Helper for one-liner | Per `clean-code`. Inline it. |
| Factory for 2 objects | Per `clean-code`. Direct instantiation. |
| Magic numbers | Per `clean-code`. Named constants. |
| God functions | Per `clean-code`. Split by responsibility. |
| Mixed concerns in one commit | Unreviewable; rollback is all-or-nothing. |
| "I'll add the test later" | No. Test first, or test in the same commit. |
| Inline secrets, even "just for now" | Per `security-review`. Critical severity. |
| "Works on my machine" without test | Unverified. Always run the project's tests. |
