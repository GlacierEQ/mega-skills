---
name: piranha-flag-retirement
description: "Delete stale feature-flag code with Piranha across JVM, Objective-C, Swift, JS/TS, and Python: given a flag name and its treatment/control values, remove dead branches and clean up the surrounding control flow."
---

# Piranha Flag Retirement

Operate Piranha as the estate's stale-flag deletion specialist: configure flag name, treated and control values, run the cleanup, and verify the resulting code compiles and tests green with the flag fully gone.

## Workflow

1. Record the retirement decision: flag, treated outcome, decision source, and date.
2. Inventory flag call sites; confirm the codebase's flag API shape matches the Piranha configuration.
3. Configure Piranha (flag name, treated/control values, API rules); dry-run or run on a copy for the first flag in a codebase.
4. Apply; compile and run the focused tests, then the broader suite.
5. Prove absence: zero references to the flag remain; remove the flag from the flag-management system as a separate recorded step.
6. Emit the flag retirement receipt: flag, decision source, files changed, compile/test results, absence proof.

## How the cleanup works

Piranha (source: `uber/piranha`, **Apache-2.0** — usable with attribution; verified 2026-10-21) automates deletion of code related to stale feature flags. Given the flag's name, its *treated* value (the behavior that stays), and its *control* value (the behavior that dies), it rewrites conditionals, removes the dead branch, deletes now-unused flag plumbing, and simplifies the result.

- **The decision precedes the tool.** Piranha assumes the rollout question is settled. Record who decided the flag is stale and the treated outcome before configuring anything.
- **Configuration is per-codebase.** Flag API shapes differ (method calls, annotations, wrapper types); Piranha's rule configuration must match the codebase's actual flag API — verify against real call sites.
- **Cleanup is verified by absence.** After the run: the flag name has zero references, the build compiles, and the suite passes. Leftover references mean hand cleanup under deprecation-removal, not a re-run.

## Safety gates

- Never run Piranha on a flag whose rollout state is assumed rather than recorded.
- Never let the tool's diff merge without reading it — automated cleanup can strand comments, tests, and config that reference the flag.
- Flag-system removal and code removal are separate recorded steps; conflating them loses the audit trail.

## Output contract

- Piranha cleanup diff with dead branches removed
- Flag retirement receipt with compile/test results and zero-reference proof

## Related skills

- deprecation-removal — the retirement discipline that orchestrates this engine
- automated-code-refactoring — bounded-batch discipline shared by all transform engines
- verification-before-completion — absence claims require command output

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/piranha-flag-retirement/tests -v
git diff --check
```
