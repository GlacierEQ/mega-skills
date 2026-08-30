---
name: codemaster
description: 'The coding-orchestration playbook. Recipes for the recurring task types:
  add a feature, fix a bug, refactor, review a PR, debug a test failure. Each recipe
  is a procedure with pre-flight, in-flight, and post-flight rituals. Use this when
  you start any coding work that involves more than one trivial edit, when you don''t
  know which skill to load, or when you want a single source of truth for ''how we
  do code here.'''
version: 0.1.0
---

# CodeMaster — The Coding Playbook (v2)

This skill is a **procedure**, not a persona. It tells you what to do, in
what order, with which skill, and how to verify.

**Load first** for any non-trivial coding task. Pair with `clean-code` for
style and `code-review-checklist` for review work.

## Environment Reality (Read This First)

Tools that are **actually installed** in this workspace:

- `python3` (3.14.6), `pytest`, `unittest` (stdlib)
- `node`, `npm`, `bun` (JS/TS)

Tools that are **NOT installed** but are referenced in some skills/docs:

- `ruff`, `mypy`, `black`, `flake8` — referenced in job-app-helix docs but absent from PATH
- `~/.claude/skills/...` scripts — Claude-Code-specific, not present here
- VS Code extensions, language servers, etc.

**Implication:** When this skill says "run the linter", it means the
project-specific check that the project *actually* has. If the project has
none, that step is a no-op with a note in the diff/PR, not a failure.

## Project Table (Canonical Test Commands)

| Project | Test command | Notes |
|---------|--------------|-------|
| `/root/projects/make-it-heavy` | `cd /root/projects/make-it-heavy && python -m unittest discover tests` | Multi-agent swarm. `clean-code` for tool/style. |
| `/root/projects/mastermind` | `cd /root/projects/mastermind && python -m pytest tests/ -v` | APEX runtime. Identity strict by default. Receipt chain mandatory. |
| `/root/projects/job-app-helix` | `cd /root/projects/job-app-helix && python -m pytest -q` | Job application engine. Largest test surface (103 test files). |
| `/root/projects/monolith` | `cd /root/projects/monolith && python -m pytest tests/ -v` (4 test files) | Meta-layer. Catalog + propagation. APEX doctrine. |
| `/root/projects/GlacierEQ_Swarm/the-tower-of-babel` | `cd /root/projects/GlacierEQ_Swarm/the-tower-of-babel && pytest` (22 test files) | Tower doctrine. **Always run `tower preflight` before any change.** Never hand-edit registry/index/generated files. |

If the project you're in isn't listed, check its `AGENTS.md` or `README.md` for
the test command. If neither has one, **ask the user** before running anything.

## The 5 Recipes

Each recipe is in `references/`. Three rituals each: **pre-flight**, **in-flight**, **post-flight**.

| # | File | When |
|---|------|------|
| 00 | `references/00-shared-rituals.md` | Pre/in/post-flight shared by all 5 recipes. Read this once. |
| 01 | `references/01-add-a-feature.md` | "Add X", "I need Y", "Build me Z", "Support W" |
| 02 | `references/02-fix-a-bug.md` | "X is broken", "Y used to work", "Crashing", "Tests failing" |
| 03 | `references/03-refactor.md` | "Clean this up", "Rename X to Y", "Extract this into a module" |
| 04 | `references/04-review-a-pr.md` | "Look at this PR", "Review this diff", "Is this safe to merge?" |
| 05 | `references/05-debug-a-test-failure.md` | "Test is failing", "Why is pytest yelling", "Flaky test" |

If you don't know which recipe applies, walk the shared pre-flight in
`00-shared-rituals.md`; the right recipe will surface.

## The Single Most-Important Rule

**Edit the file + all dependent files in the same task.**

Before changing anything:

1. `grep` who imports the file you're about to edit
2. `grep` what the file imports
3. `grep` what tests cover the file
4. Note all of them
5. Make all changes together
6. Run all affected tests together

A "successful" edit that leaves a broken import is a failure. Per
`clean-code`: "Edit the file + all dependent files in the SAME task. Never
leave broken imports or missing updates."

## Universal Definition of Done

All 5 recipes have a recipe-specific DoD. This is the **floor** that applies
to every coding task. If any of these fail, you're not done.

- [ ] **Code complete.** The change matches the stated intent from pre-flight.
- [ ] **Tests pass.** The project's test command runs green. Document the count.
- [ ] **No broken imports.** Every `from X import Y` resolves. Every caller
      of every changed function still type-checks against the new signature.
- [ ] **No silent behavior changes.** Any public function whose contract
      changed has updated docstring + tests + callers in the same commit.
- [ ] **No secrets in code.** Nothing in the diff matches
      `sk-`, `ghp_`, `github_pat_`, `eyJ`, `-----BEGIN`, `pcsk_`, `pplx-`,
      `hf_`, `ntn_`, or any literal from `/root/.vault_env`. Per
      `security-review`.
- [ ] **No drive-by changes.** The diff is exactly the task and nothing else.
- [ ] **Receipts if the project requires them.** APEX-family projects
      (`mastermind`, `monolith`) append a receipt on every state change.
      `make-it-heavy` logs to `agent_runs` and `tool_calls`. Tower does
      its own integrity/receipt flow. Other projects: no-op.
- [ ] **Stated in one paragraph.** "Changed X to do Y. Verified: tests A,
      B, C pass; project test command ran N tests green; no secrets in
      diff; dependents D, E still resolve." That paragraph is in the
      final message.

## Hard Rules (Apply to All Recipes)

1. **Read before write.** Never edit a file you haven't read in this session.
2. **One logical change per commit.** Mixed changes are unreviewable.
3. **Test must pass before "done."** "I think it works" is not done.
4. **No silent behavior changes.** See the universal DoD above.
5. **Secrets never enter code.** Per `security-review` and rule 5 of the
   DoD. The vault is at `/root/.vault_env`; do not inline, log, or commit.
6. **Receipts for state changes** — only when the project requires them.
   Default: no-op. APEX-family and tower: required. Other projects:
   write to the project's own audit log if one exists.
7. **Run the project's test command, not yours.** See the project table
   above. The project knows its test command; you don't.
8. **For tower-of-babel: run `tower preflight` before any non-trivial
   change.** This is non-negotiable per the tower AGENTS.md. Skipping
   it is a Doctrine violation.

## When to Stop and Ask the User

Recipes say "ask if X is unclear". Make that explicit:

- **Pre-flight can't form a one-sentence description of the change.** Stop.
- **Pre-flight can't list the tests that must pass.** Stop. (No test plan
  = no completion criterion = open-ended work = bad.)
- **The right test command isn't in the project table and not in the
  project's AGENTS.md / README.** Stop.
- **The change requires rotating or adding a secret.** Stop. Per
  `security-review`.
- **The change crosses a project boundary** (e.g. editing mastermind from
  inside make-it-heavy). Stop and confirm.
- **The change is a "while I was here"** — noticed something else needs
  fixing while doing the actual task. Don't fix it; note it; ask the user.

## When This Skill Doesn't Apply

- **Documentation-only changes** (no code touched) → just `clean-code` for
  style. Skip the rituals; the universal DoD is overkill.
- **Pure refactor with zero behavior change** → still use `03-refactor` and
  the universal DoD; "no behavior change" is what the test suite proves.
- **One-line typo fix** → read the file, fix the typo, run the project's
  test command. The full pre-flight is overhead here; the post-flight DoD
  is still binding.

## When to Update This Skill

- A new project is added with a non-standard test command → add to the
  project table.
- A new recurring task type emerges (e.g. "migrate database schema",
  "add CLI subcommand") → add a `references/0X-…` recipe.
- A recipe is consistently failing in practice → fix the recipe, don't
  edit around it.
- The skill count in `master/SKILL.md` drifts → update the description's
  wording; don't hardcode a number, say "current count" in cross-references.
