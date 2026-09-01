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

1. Identify the concrete outcome, inputs, and constraints.
2. Inspect relevant project state or artifacts before making changes.
3. Load only the bundled resources needed for the current task.
4. Execute the narrowest complete workflow that produces the requested outcome.
5. Verify the result with observable output, tests, or source-backed evidence.
6. Report the produced artifact or exact resulting state. Never claim execution that did not occur.

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
