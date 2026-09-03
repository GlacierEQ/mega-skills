# Capability Hierarchy and Mega-Skill Pyramid Contract

## Purpose

Mega-Skills is a capability compiler: real Skills compound into larger proper Skills until an end-to-end Mega Skill exists as the apex of a validated workflow pyramid. The hierarchy must increase operational capability without erasing the identity, validation, provenance, or outputs of the Skills below it.

## Prime ontology

**Everything in the pyramid is a Skill.** The labels atomic, compound, and mega describe scale and composition, not whether the object is a proper Skill.

```text
                           MEGA SKILL
                 end-to-end workflow / pipeline
                     /          |          \
            COMPOUND SKILL  COMPOUND SKILL  COMPOUND SKILL
              /    |    \       /   \          /   |   \
          SKILL  SKILL  SKILL  SKILL SKILL     SKILL SKILL SKILL
```

A Mega Skill is therefore **not** a flat router over prose stages. It is a hierarchical representation of complete, real capability assembled from real Skill building blocks.

## Skill kinds

### 1. Atomic Skill

An **Atomic Skill** is the smallest maintained, independently useful procedure. It lives under `skills/<skill-id>/`, includes `SKILL.md`, and owns a trigger/use condition, input contract, method, output contract, and local validation.

### 2. Compound Skill (Combo Skill compatibility layer)

A **Compound Skill** is a proper reusable Skill whose implementation is a bounded composition of lower Skills. Existing `combo-skills/<combo-id>/COMBO.md` manifests are the compatibility/source representation for this class. A Compound Skill must have its own selection condition, ordered execution contract, handoffs, compound artifact, quality gate, and independent acceptance criteria.

It does not copy the implementation of its children; it composes them.

### 3. Mega Skill

A **Mega Skill** is a proper end-to-end Skill at mission scale. It is the apex of a hierarchy of Compound and Atomic Skills. It owns the complete workflow/pipeline contract: mission trigger, route selection, durable state, phase gates, cross-branch integration, recovery, final acceptance, and mission output.

A Mega Skill is valid only when its full dependency pyramid resolves to real Skill identities (or explicitly typed external Skill references), and every intermediate composition is itself independently valid as a Skill.

## Dependency law

```text
Atomic Skill ──► Compound Skill ──► Mega Skill
     │                 │                │
     └──── proper Skill identity at every level ────┘
```

Composition points upward. No lower Skill depends on the mission-scale parent merely to remain valid. Shared Skills may feed more than one Compound Skill, so the machine representation is a DAG even when the human representation is drawn as a pyramid.

## Pyramid invariants

1. **Real-node invariant.** Every GlacierEQ-owned node resolves to a canonical registry entry and source path.
2. **Proper-Skill invariant.** Atomic, Compound, and Mega nodes each own a trigger/use condition, input/output contract, and validation boundary appropriate to their scale.
3. **No-copy invariant.** Parents reference child Skill IDs and artifacts; they do not duplicate child methods.
4. **Compounding invariant.** Every parent adds integration capability that no child owns alone.
5. **Artifact invariant.** Every edge describes a real handoff or dependency and every composition emits a traceable artifact.
6. **Validation invariant.** A Mega Skill cannot be active if required child Skills or Compound Skills are unresolved or invalid.
7. **Provenance invariant.** Source identity and lower-layer evidence survive every composition step.
8. **Context invariant.** Higher scale does not authorize loading unrelated context or silently broadening scope.

## Machine-readable pyramid

`registry/mega-skill-pyramids.json` is generated from the canonical registries by:

```bash
python scripts/generate_mega_skill_pyramids.py
python scripts/generate_mega_skill_pyramids.py --check
```

The generated projection resolves every Mega Skill into:

- level 0: one Mega apex Skill;
- level 1: its required and conditional Compound workflow Skills;
- level 2: the Atomic or explicitly external Skill building blocks used by those Compound Skills;
- typed edges describing required/conditional composition and child roles.

The projection is generated, not hand-maintained. Canonical ownership remains in `skills.json`, `combo-skills.json`, and `mega-skills.json`.

## Current registry state — 2026-09-03

At the revision that introduced the pyramid contract:

- **709** registered Atomic Skills;
- **33** registered Compound workflow Skills;
- **29** registered Mega Skills;
- **123** internal Compound→Atomic Skill references, all resolving to registered Skills;
- **10** explicitly typed external-skill references;
- every Mega→Compound reference resolves.

These are registry/object counts, not claims of production deployment or external adoption.

## Snowball acceptance test

| Test | Atomic Skill | Compound Skill | Mega Skill |
|---|---|---|---|
| Proper Skill identity | Required | Required | Required |
| Trigger/use condition | Required | Required | Required at mission scope |
| Input/output contract | Required | Required | Required |
| Reuses child IDs without copying methods | N/A | Required | Required |
| Adds new value | Procedure | Composition + handoff | End-to-end integration + durable mission state |
| Traceable artifact | Atomic artifact | Compound artifact | Mission result + durable handoff |
| Independent validation | Required | Required | Required |
| Source/provenance preservation | Required | Required | Required |

## Snowball cycle

```text
verified atomic Skill artifact
        ↓
proper Compound Skill + explicit handoffs
        ↓
verified compound workflow artifact
        ↓
Mega Skill pyramid + conditional mission integration
        ↓
evidence-backed end-to-end result + durable resume state
        ↓
observed evidence improves future Skill composition
```

## Cross-layer source preservation invariant

No higher Skill may gain convenience by destroying lower-layer source meaning.

```text
original source / journal / evidence
        ↓ immutable provenance
Atomic Skill artifact
        ↓ additive method
Compound Skill artifact
        ↓ additive composition
Mega Skill mission state
```

A Compound or Mega Skill may compact, route, rank, annotate, or supersede an analysis artifact, but it may not silently rewrite the underlying source. If a later layer discovers an error, preserve the old artifact/proposition and record the correction, evidence, and effective supersession explicitly.
