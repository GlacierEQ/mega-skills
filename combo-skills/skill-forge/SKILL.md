---
name: skill-forge
description: 'Combo Skill: Skill Forge. Reusable capability chain.'
---

# Skill Forge

Use this Combo when a proven task pattern should become a reusable atomic Skill. It composes `mission-contract`, `evidence-register`, `skill-creator`, and `quality-gate` without duplicating their individual methods.

| Order | Member | Compound contribution |
|---:|---|---|
| 1 | `mission-contract` | Defines the desired capability, trigger, scope, and non-goals. |
| 2 | `evidence-register` | Preserves real use cases, source material, and observed failure modes. |
| 3 | `skill-creator` | Authors, packages, and validates the reusable Skill. |
| 4 | `quality-gate` | Confirms that the package is specific, concise, and independently useful. |

The output is `validated-skill-package.skill` with a registry-ready Skill contract. It must include a named trigger, reusable method, local validation, owner, and semantic version before the Mega layer can select it.
