# 02 — Fix a Bug

The most over-confident task. The bug is rarely where the symptoms appear.

> **After this recipe, also walk the Universal Definition of Done in
> `codemaster/SKILL.md`.** It's the floor that applies to every coding task.

## When to Use

User says: "X is broken", "Y used to work, now it doesn't", "This is giving
the wrong answer", "It's crashing", "Tests are failing".

## Pre-Flight (Recipe-Specific Additions)

After the shared pre-flight, also:

1. **Reproduce the bug first.** If you can't reproduce it, you can't fix
   it. Write a failing test that demonstrates the wrong behavior. This test
   stays as a regression test after the fix.
2. **Find the symptom, not the cause (yet).** Where does the wrong value
   actually surface? Note the file, line, and the value.
3. **Hypothesize, don't guess.** Form 2–3 candidate root causes before
   looking. Examples:
   - "The input isn't what I think it is"
   - "The dependency was updated and changed behavior"
   - "The state from a previous step is leaking in"
   - "The edge case isn't handled"
4. **For intermittent bugs:** check if it's actually intermittent or just
   under a specific condition. Add timing/concurrency/size to your mental
   model.

## In-Flight (Recipe-Specific)

1. **Fix at the root cause, not the symptom.** Suppressing an error to make
   it "go away" is not a fix. Trace back until the fix is at the place
   where the wrong value is *created*, not where it's *observed*.
2. **One fix, one commit.** Don't bundle the fix with a refactor.
3. **Don't expand scope.** A bug fix changes behavior to match the spec.
   It does not "while I'm here" improve performance or add features.
4. **Preserve the failing test.** Make it pass; do not delete it. It is
   your regression guard.

## Post-Flight (Recipe-Specific)

Definition of done for "fix a bug":

- [ ] Failing test reproduces the bug
- [ ] Failing test now passes after the fix
- [ ] Other tests still pass (no regressions)
- [ ] Root cause is documented in the commit message or PR description
- [ ] No "suppress error" / "try/except pass" patterns in the diff
- [ ] Shared post-flight: diff reviewed, project tests pass, lint clean

## Debugging Strategy (When You Don't Know the Cause)

Use this if the bug isn't obvious from the failing test:

1. **Read the actual error output.** The full traceback, not the last line.
2. **Add a print/log of the input** at the failing function. Confirm the
   input is what you expect.
3. **Bisect.** If "it used to work", find the commit that broke it:
   `git log --oneline -- <file>` → `git checkout <commit>` → run test.
4. **Simplify the input.** Reduce the failing case to the strong and smart reproducing input
   that still fails. Often reveals the cause immediately.
5. **Check the environment.** Library versions, env vars, file system
   state. Bugs that "only happen on my machine" are usually environmental.

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fixed the symptom, bug returns | Root cause not addressed | Trace one level up; fix where the wrong value is *created* |
| Fix breaks 3 other tests | Side effect or shared state | The fix is too broad; narrow it. Or update the other tests' expectations if the contract genuinely changed. |
| Bug is intermittent | Race condition, time-of-check/time-of-use, env-dependent | Reproduce reliably first; if you can't, the bug isn't understood yet |
| "Fixed" but the test was the wrong test | Test asserted the wrong thing | Fix the test, then fix the bug |
| Fix only works for one input | Hardcoded for the case you saw | Parametrize; add tests for the other cases |

## Related Skills

- `reasoning-variants/references/99-debugging.md` — agent-reasoning failures
- `clean-code` — error handling style
- `architecture` — if the bug exposes a design flaw
