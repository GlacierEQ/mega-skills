# 05 — Debug a Test Failure

The most-frustrating task. The test is right, the code is right, and yet.

> **After this recipe, also walk the Universal Definition of Done in
> `codemaster/SKILL.md`.** Once the test passes, the DoD gates the fix.

## When to Use

User says: "This test is failing", "Why is pytest yelling at me", "Test
was passing yesterday", "Flaky test", "Can't reproduce locally".

## Hard Rule

**Read the failure first. Then the test. Then the code. In that order.**

Many debugging hours are lost because people start by reading the
implementation and try to guess what's wrong. The failure message is the
most direct evidence you have.

## Pre-Flight (Recipe-Specific Additions)

After the shared pre-flight, also:

1. **Run the failing test in isolation.** Not the full suite. `pytest
   tests/test_x.py::test_specific -v` or `python -m unittest
   tests.test_x.TestClass.test_method -v`. Confirm it still fails
   the same way.
2. **Capture the *full* output.** Not the last 5 lines. Run with `-v` or
   `--tb=long`. Save it if it's long. The information is usually in the
   middle, not at the top or bottom.
3. **Identify the failure shape.** Which of these is it?
   - **AssertionError** — code produced wrong value; check expected vs actual
   - **ImportError / ModuleNotFoundError** — missing dep or broken path
   - **TypeError / AttributeError** — wrong API used, or API changed
   - **TimeoutError** — test took too long; likely infinite loop or slow I/O
   - **PermissionError** — file/network/auth issue, not a logic bug
   - **Flaky** — sometimes passes, sometimes fails (subcategory below)

## In-Flight (Recipe-Specific — Per Failure Shape)

### AssertionError

1. Print or log the actual values. If the assertion message is unhelpful,
   make it helpful: `assert x == y, f"x={x!r}, y={y!r}"`.
2. Find where `x` is computed. That's where the bug is.
3. If `x` is a chain of transformations, bisect: print the value after
   each transformation.

### ImportError / ModuleNotFoundError

1. Check the import path. Is it `from x.y import z` but the file is at
   `x/w/y.py`? The error tells you what it tried.
2. Check `sys.path`. Some projects need `PYTHONPATH=.` or a conftest
   that adds `src/` to the path.
3. Check that the dependency is installed. `pip list | grep <name>`.
4. Check for circular imports. If module A imports B imports A, you
   get this at import time.

### TypeError / AttributeError

1. The error tells you the *type* and the *attribute*. The bug is at
   the call site, not in the type's definition.
2. Print the type: `print(type(x))`. Confirm it's what you think.
3. If the type changed recently, check the version. `pip show <dep>`.
4. If `None` is involved, trace back: where did the `None` come from?

### TimeoutError

1. Add a print at the start of every loop or blocking call. Find which
   one never returns.
2. Check for `while True:` without a break. Add an iteration counter.
3. Check for blocking I/O without a timeout.

### PermissionError

1. Read the message. It says which path. Check perms: `ls -la <path>`.
2. If it's a temp dir, check `TMPDIR` env var and whether it exists.
3. If it's a network call, check the URL and the creds.

### Flaky

1. **First, prove it's flaky.** Run 10 times: `for i in {1..10}; do
   pytest tests/test_x.py::test_specific; done`. If 7/10 pass, it's flaky.
2. **Then find the order dependence.** Run the test with `pytest -p
   no:randomly` and with the full suite. If the test passes alone but
   fails in the suite, it's order-dependent.
3. **Common causes:**
   - Shared global state (a module-level dict, a singleton, a DB)
   - Time-of-day dependence (the test compares `now()` to a hardcoded value)
   - File system leaks (the test creates a file, doesn't clean up)
   - Port collisions (the test binds a fixed port)
4. **Fix by isolation, not retries.** Per `clean-code`: `max_retries` is
   a smell, not a fix. Add a `tearDown` / `fixture(finalizer)`.

## Post-Flight (Recipe-Specific)

Definition of done for "debug a test failure":

- [ ] Failure reproduced
- [ ] Root cause identified (not "I added a try/except")
- [ ] Fix is in the right place (not the test, unless the test was wrong)
- [ ] Test now passes deterministically (run 10× to prove for flaky ones)
- [ ] Other tests still pass
- [ ] If the test was wrong, that's documented in the commit message
- [ ] Shared post-flight: diff reviewed, project tests pass

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Works on my machine" | Environment diff (deps, env vars, OS) | Match CI's environment exactly; or fix the test to not depend on environment |
| Fixed by adding sleep | Race condition, not understood | Use a real synchronization primitive; document why |
| Fixed by retry | Test is order-dependent | Find the shared state; isolate it |
| Fixed by deleting the test | Gave up | Don't. If the test is wrong, fix the test. If the test is right, fix the code. |
| Fixed by mocking | Test was integration, became unit | Be explicit. If it's a unit test now, name it accordingly. |
| Worked, then broke after a library upgrade | Library changed behavior | Pin the version, or adapt to the new behavior. Document the choice. |

## Related Skills

- `reasoning-variants/references/99-debugging.md` — agent-reasoning failures
  (different problem class; load if the test failure is the agent's fault)
- `clean-code` — function/style patterns that prevent common test failures
- `architecture` — if the test failure exposes a design issue
