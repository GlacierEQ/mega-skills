# Capability Hierarchy and Snowball Contract

## Purpose

The hierarchy makes composite intelligence stronger without making context larger or ownership blurrier. Every level must add a new type of value: method, composition, or mission integration.

## Layer contracts

### 1. Skills

A **Skill** is the smallest maintained, independently useful procedure. It lives under `skills/<skill-id>/`, includes `SKILL.md`, and owns its trigger, method, local artifact, and local validation. A Skill may use references, templates, and deterministic scripts, but it may not depend on a Combo or Mega Skill.

### 2. Combo Skills

A **Combo Skill** is an explicit repeated route across multiple Skills. It lives under `combo-skills/<combo-id>/`, includes `COMBO.md`, names every member by ID, declares dependency order, turns each boundary into an input/output contract, and produces a compound artifact. It does not own copies of its member methods.

### 3. Mega Skills

A **Mega Skill** is a conditional mission system. It lives under `mega-skills/<mega-id>/`, includes `MEGA.md`, chooses Skills and Combo Skills based on mission shape, and owns durable state, phase gates, exception handling, and cross-artifact integration. It does not silently invoke unrelated capability.

## Dependency law

```text
Skills ─────────► Combo Skills ─────────► Mega Skills
   ▲                    ▲                       │
   └── may not depend ──┴── may not depend ─────┘
```

Dependencies can only point upward. An external/platform skill is always treated as an atomic capability reference unless deliberately adopted as a GlacierEQ-owned Skill.

## Snowball acceptance test

| Test | Skill | Combo Skill | Mega Skill |
|---|---|---|---|
| Independent trigger is defined | Required | Not required | Required at mission scope |
| Reuses lower-layer IDs without copying their methods | Not applicable | Required | Required |
| Adds new value | Procedure and local validation | Ordering and handoff contract | Conditional routing, state, phase gates, integration |
| Produces a traceable artifact | Atomic artifact | Compound work packet | Mission result plus durable handoff |
| Can be validated independently | Required | Required | Required |
| Loads only required context | Required | Required | Required |

If a proposed object cannot pass this test, it is either a duplicate, an unproven idea, or a documentation section—not a new Skill layer.

## Snowball cycle

```text
verified atomic artifact → reusable capability chain → compound artifact
→ conditional mission route → durable state and final integration
→ evidence that improves future Skill and Combo design
```

Do not mutate a lower-level contract during an active mission without a decision record and fresh validation of dependent Combo and Mega entries.
