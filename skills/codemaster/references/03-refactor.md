# 03 — Refactor

The most-likely-to-go-wrong task. Refactors that change behavior are not
refactors.

> **After this recipe, also walk the Universal Definition of Done in
> `codemaster/SKILL.md`.** It's the floor that applies to every coding task.

## When to Use

User says: "Clean this up", "Rename X to Y", "Extract this into a module",
"This function is too big", "The structure is wrong".

## Hard Rule

**A refactor changes structure without changing behavior.** If behavior
changes, it's not a refactor; split it. This is non-negotiable.

## Pre-Flight (Recipe-Specific Additions)

After the shared pre-flight, also:

1. **Confirm the test suite passes *before* you start.** A refactor is only
   safe if you have a green baseline. If tests are failing, fix them first
   (use recipe 02).
2. **Identify the contract.** What does this code *promise* to callers?
   Inputs, outputs, exceptions, side effects, performance. Write it down
   in one paragraph. The refactor must preserve this.
3. **Scope the refactor.** One rename, one extraction, one module move.
   Not all of them in the same commit.
4. **For rename / move:** check every reference. `grep -rn "<old_name>"`.
   Update callers, tests, docs, configs, in one pass.

## In-Flight (Recipe-Specific)

1. **Make the change mechanical.** If you're renaming, rename. If you're
   extracting, extract. Resist the urge to "improve" while you're there.
2. **Run tests after each step.** Don't batch five refactor steps and run
   tests at the end. One step, test, next step.
3. **Keep diffs small.** A 500-line refactor is unreviewable and likely
   to contain accidental behavior changes. 50 lines or less per commit
   is a good target.

## Post-Flight (Recipe-Specific)

Definition of done for "refactor":

- [ ] All tests that passed before still pass (behavior preserved)
- [ ] No callers reference the old name/path
- [ ] No "while I was here" changes in the diff
- [ ] Shared post-flight: diff reviewed, project tests pass, lint clean
- [ ] For APEX projects: any moved capability is still in the receipt chain

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Refactor" changed behavior | Scope creep | Split. Behavior change is a separate commit. |
| Tests pass but reviewers find issues | Diff is too large to review | Smaller commits. One rename or one extraction per commit. |
| Renamed but old name still works | Half the references updated | `grep` again, finish the rename in this commit. |
| "Cleaner" but slower | Different algorithmic complexity | Re-run benchmarks; if the project has none, add a quick micro-benchmark. |
| Module structure makes sense in isolation but breaks the public API | Refactor moved a public symbol | Re-export, or treat as a breaking change with a major version bump. |

## Refactor Smells (When to Suggest One)

| Smell | Refactor |
|-------|----------|
| Function > 20 lines | Extract smaller functions, each doing one thing |
| Same code in 2+ places | Extract to a shared helper, not "DRY for DRY's sake" — extract only if the duplication is the *same intent* |
| Module > 500 lines | Split by responsibility. Use the file's existing structure as a guide. |
| 5+ args to a function | Bundle into a dataclass; per `clean-code`: max 3 args, prefer 0–2 |
| Deep nesting (3+ levels) | Guard clauses, per `clean-code` |
| Magic numbers | Named constants at module top |
| Unused imports / dead code | Delete. YAGNI. |

## Related Skills

- `clean-code` — function size, naming, nesting
- `architecture` — if the refactor crosses module boundaries
- `code-review-checklist` — review your own refactor as if you didn't write it
