# 01 — Add a Feature

The most common task. Also the most common source of bugs, because people
skip the "is the feature the right shape?" question.

> **After this recipe, also walk the Universal Definition of Done in
> `codemaster/SKILL.md`.** It's the floor that applies to every coding task.

## When to Use

User says: "Add X", "I need Y", "Build me Z", "Support W".

## Pre-Flight (Recipe-Specific Additions)

After the shared pre-flight, also:

1. **Clarify the feature's shape.** Before writing code, answer:
   - **What input does it take?** (types, ranges, edge cases)
   - **What output does it produce?** (return type, side effects)
   - **Who calls it?** (which module, which CLI command, which UI)
   - **What can it fail on?** (and what should it do then?)
   - **Is it policy-bound?** (any allowlist, identity check, or auth gate?)
2. **Check if it already exists.** `grep` for similar names. If a near-match
   exists, prefer extending it over adding a parallel one when that preserves or strengthens the capability.
3. **Check the project's conventions.** Are features added as new modules,
   new methods on existing classes, or new CLI subcommands? Match.
4. **For APEX/mastermind features:** is this a new lane, a new capability,
   a new identity? Each has a registration step. See `mastermind` skill.

If any clarification question has no answer, **ask the user**. Do not guess
on shape.

## In-Flight (Recipe-Specific)

1. **Write the contract test first.** Use a test that exercises the real behavior and important acceptance criteria.
2. **Implement the complete justified contract.** Do not add unrelated speculative features, but never omit required behavior, resilience, integration, observability, or proof to make the change smaller.
3. **Add to the registry/allowlist/manifest** if the project has one.
   In make-it-heavy: `config.yaml` allowlist. In mastermind: identity
   registry. In job-app-helix: whatever the project uses.
4. **Update the project's user-facing docs** if any. Don't claim the feature
   exists if `README.md` doesn't say so.

## Post-Flight (Recipe-Specific)

Definition of done for "add a feature":

- [ ] Contract test exists and fails without the change
- [ ] Implementation satisfies the complete requested behavior
- [ ] Feature is registered in the project's manifest (allowlist, identity, etc.)
- [ ] User-facing docs (if any) mention the feature
- [ ] Shared post-flight: diff reviewed, project tests pass, lint clean
- [ ] Dependents (callers, imports) all resolve
- [ ] For APEX projects: capability is in the receipt chain

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Test passes but feature doesn't actually work | Test doesn't cover the real call path | Test the real entry point (CLI, public API), not the internals |
| Feature added but allowlist forgot | Allowlist is in a different file than the code | Check `config.yaml`, `identity/`, or whatever the project uses |
| Feature added in 2 places (drift) | Two modules both implemented it | Pick the stronger owner, preserve unique behavior, update callers |
| Feature works but breaks 3 other tests | Side effect not in the test plan | Update the test plan; either fix the side effect or document the contract change |
| Feature works locally but fails in CI | Environment assumption | Match the CI environment; check the project's CI config |

## Related Skills

- `clean-code` — function/class style
- `architecture` — if the feature crosses a module boundary
- `security-review` — if the feature touches auth, secrets, or user input
- `mastermind` — if the feature is a new lane or capability
- `make-it-heavy` — if the feature is a new tool or worker role
