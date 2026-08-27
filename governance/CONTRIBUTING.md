# Contributing to GlacierEQ Mega Skills

## Choose the correct layer first

Before creating anything, inspect the registries and answer three questions: Is this an independently useful procedure? Is it a recurring ordered composition? Or does it conditionally route a long-horizon mission while owning state and integration?

| If the answer is… | Add… | Required artifact |
|---|---|---|
| An independently useful procedure with its own trigger and local check | A **Skill** | `skills/<id>/SKILL.md` |
| A repeated sequence of two or more Skills with a stable handoff | A **Combo Skill** | `combo-skills/<id>/COMBO.md` |
| A conditional mission system using one or more Combo Skills and durable state | A **Mega Skill** | `mega-skills/<id>/MEGA.md` |

## Required change sequence

1. Inspect the relevant lower-layer contracts and registry entries.
2. Write a decision record if the change affects ownership, dependencies, ID stability, layer classification, or compatibility.
3. Add the package or composition contract in its layer directory.
4. Add the matching registry entry, including artifact, inputs, outputs, and validation.
5. Confirm dependency direction is upward only: Skills → Combo Skills → Mega Skills.
6. Run `python scripts/validate_hierarchy.py` and `python -m unittest discover -s tests -v`.
7. Submit the smallest coherent change for review.

Reviewers must reject a change if it copies lower-level instructions into a higher-level body, lacks a new artifact, creates a circular dependency, misstates external ownership, creates an empty placeholder package, or expands an active mission’s contract without a decision record.
