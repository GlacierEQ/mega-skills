# 04 — Review a PR (or a Diff)

The most-skipped task. People skim and approve.

> **After this recipe, also walk the Universal Definition of Done in
> `codemaster/SKILL.md`.** The DoD applies to the *change*, not to the
> review; use it as the bar the change must clear.

## When to Use

User says: "Look at this PR", "Review this diff", "Is this safe to merge?",
"What do you think of this change?".

## Pre-Flight (Recipe-Specific Additions)

After the shared pre-flight, also:

1. **Read the PR description first.** What problem is this solving? What
   approach was chosen? What was rejected? Without this, the diff is
   unmappable.
2. **Read the diff, not the file.** `git diff <base>...<head>`. If the
   diff is > 400 lines, ask whether it should be split (recipe 03).
3. **Check the test diff.** Is there one? Are new tests covering the
   new behavior, or only the old behavior?
4. **Check the project context.** Which project, which module, which
   conventions. Load the project skill if one exists.

## In-Flight (Recipe-Specific — The Review Itself)

Walk the diff in this order. Don't go in file order; go by risk.

### 1. Correctness

- Does the code do what the PR description says?
- Are the right inputs handled? Edge cases?
- Are errors handled correctly (or at all)?
- Is concurrency safe if applicable?
- For APEX projects: does this change the receipt chain in a way the
  runtime expects?

### 2. Tests

- Is there a test for each new public function or behavior change?
- Are the tests specific (asserting the right value), not just "didn't crash"?
- Do the tests cover the error path, not just the happy path?
- Are any tests deleted? Why? Is the deletion justified?

### 3. Security

Per `security-review`. Watch for:

- Hardcoded secrets, tokens, URLs with creds
- User input not validated (path traversal, SQL injection, etc.)
- Auth/authz missing on a new endpoint
- Logging that includes sensitive data
- New dependency with a known CVE (check `requirements.txt` / `package.json`)

### 4. Style and Convention

Per `clean-code`:

- Function size, nesting depth, naming
- Existing style respected (don't impose new style in a PR)
- Comments only when naming can't carry the meaning
- No dead code, no debug prints, no commented-out blocks

### 5. Scope

- One logical change per PR
- "While I was here" changes are a red flag — note them, ask for removal
- Unrelated refactors mixed with feature/fix work

## Post-Flight (Recipe-Specific)

A review ends with one of four verdicts:

1. **Approve** — no blocking issues, no nits worth blocking
2. **Comment** — questions or non-blocking suggestions
3. **Request changes** — at least one blocking issue; list them
4. **Reject** — fundamental design problem; needs redesign before re-review

State the verdict and the reasoning in one paragraph. Be specific:
not "looks good" but "approve: tests cover happy and error paths,
no secrets, matches existing style".

## The Self-Audit

After writing the review, before submitting:

- [ ] Did I read the PR description, not just the diff?
- [ ] Did I check the tests?
- [ ] Did I run the project's tests locally if the PR touched test files?
- [ ] Are my comments specific and actionable?
- [ ] Did I avoid bikeshedding (style preferences, naming debates)?
- [ ] Is my verdict one of the four, and is it justified?

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Approved a PR that broke things | Skimmed the diff | Walk the diff in risk order, not file order |
| Requested 30 nits | Bikeshedding | Block on the 1–2 real issues; comment on the rest |
| Missed a security issue | Didn't run the security checklist | Always do the 5-item security pass in step 3 |
| Approved but didn't test locally | Trusted CI alone | If the PR is non-trivial, run tests locally too |
| Review took 3 hours | Diff is too large | Push back: "please split this into N smaller PRs" |

## Related Skills

- `code-review-checklist` — comprehensive checklist (444 lines; use this
  recipe for *how* to review, `code-review-checklist` for *what* to look at)
- `security-review` — load alongside this recipe
- `clean-code` — style consistency checks
- `architecture` — for structural changes
