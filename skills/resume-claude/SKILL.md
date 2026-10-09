---
name: resume-claude
description: "Resume or continue work from a recent Claude Code session. Use when the user switched from Claude Code, says \"continue from Claude\" or \"resume my Claude session\", or names a Claude session by description, path, or native ID."
---

# Resume Claude

## Purpose

Resume or continue work from a recent Claude Code session. Use when the user switched from Claude Code, says \"continue from Claude\" or \"resume my Claude session\", or names a Claude session by description, path, or native ID.

## Use When

Use this skill when the requested task matches the capability described above and this is the most specific available skill for the work.

## Operating Method

1. Recover the exact Operator objective, existing mission graph, corrections, verified gains, source pointers, and completion test.
2. Refresh relevant owning-source state and reconcile it with recovered evidence before treating a historical gap or task label as current.
3. Map affected workstreams, critical dependencies, useful independent routes, and downstream consequences; load the resources needed to cover that work.
4. Select and execute the strongest coherent workflow by outcome gain, dependency unlock, evidence value, and preservation of verified strengths. Skill ownership scopes each operation; it never shrinks the mission.
5. Verify the resulting state, propagate material corrections across affected work, and continue through reachable authorized work. A prepared next action or completed artifact is a checkpoint; completion requires the requested outcome.
6. Report the resulting outcome and observable proof, unfinished obligations, and exact continuation frontier. Never claim execution that did not occur.

## Progressive Disclosure

Keep the core procedure concise. Load detailed references, scripts, and tests only when they are needed.

### Scripts
- scripts/run.py
- scripts/this_skill.py
- skill.py

### Tests
- tests/test_resume_claude.py

## Verification

Instruction readiness and executable readiness are separate. Scripts and integrations must earn behavioral proof through the repository readiness assay before they are described as executed or behavior-verified.

## Boundaries

- Do not invent missing implementation.
- A package-discovery adapter is not evidence of domain execution.
- Preserve upstream provenance and existing project semantics.
- Report unavailable credentials, services, or destructive dependencies precisely instead of fabricating success.
