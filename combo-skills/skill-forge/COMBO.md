# Skill Forge

## Purpose

Turn a proven recurring task pattern into a compact, testable, reusable Skill package. Select this Combo only after the task has concrete examples and an independently useful method.

## Members and order

1. **`far-away-party-core`** records the desired outcome, evidence from real use, reusable boundaries, and quality gate.
2. **`skill-creator`** authors the package, uses progressive disclosure, validates its shape, and packages the deliverable.

## Handoff contract

| Boundary | Required input | Output | Validation |
|---|---|---|---|
| Pattern analysis → package design | Concrete examples, user need, known failure modes, non-goals | Skill design contract | The package adds non-obvious reusable procedure rather than generic explanation. |
| Package design → release | `SKILL.md`, references, templates, scripts as justified | `validated-skill-package.skill` | Required frontmatter, links, scripts, and resource usage pass validation. |

## Compound artifact

The output is a validated `.skill` package and decision record that identifies the trigger, owner, local tests, and version. The Mega layer may use it as a new atomic capability only after it enters `registry/skills.json`.

## Non-goals

Do not create a Skill merely because a task is large. A large task may need a Combo or Mega Skill, while a Skill must remain independently useful and specific.
