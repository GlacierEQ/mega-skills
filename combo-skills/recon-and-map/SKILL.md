---
name: recon-and-map
description: 'Combo Skill: Recon and Map. Reusable capability chain.'
---

# Recon and Map

Use this Combo when repository roles, boundaries, or relationships are uncertain before a change. It composes `mission-contract`, `repository-context-onboarding`, `evidence-register`, and `quality-gate` into one read-only inspection route.

| Order | Member | Compound contribution |
|---:|---|---|
| 1 | `mission-contract` | Fixes candidate scope, purpose, acceptance criteria, and read-only boundary. |
| 2 | `repository-context-onboarding` | Inspects roles, revisions, contracts, and tensions. |
| 3 | `evidence-register` | Separates documented claims, verified behavior, and unknowns. |
| 4 | `quality-gate` | Accepts the map only when every candidate is resolved or explicitly unresolved. |

The output is `repository-context-map.md`, including source locations, role boundaries, tensions, and the smallest next verification. It is ready for a Mega Skill only after no repository selection depends on implicit assumption or uninspected evidence.
