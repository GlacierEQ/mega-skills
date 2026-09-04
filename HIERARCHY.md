# Capability Hierarchy and Recursive Mega-Skill Pyramid Contract

## Purpose

Mega-Skills is a capability compiler: real Skills compose into larger proper Skills until a complete end-to-end Mega Skill exists as the apex of a validated workflow pyramid. The hierarchy must increase operational capability without erasing the identity, validation, provenance, artifacts, or outputs of the Skills below it.

## Prime ontology

**Everything in the pyramid is a Skill.** Atomic, compound, and mega are scale/composition kinds, not different standards of legitimacy.

```text
                                 MEGA SKILL
                         complete workflow / pipeline
                         /          |           \
              COMPOUND SKILL   COMPOUND SKILL   COMPOUND SKILL
                /      \              |             /       \
        ATOMIC SKILL   COMPOUND SKILL  ...     ATOMIC SKILL  ...
                         /      \
                  ATOMIC SKILL  ATOMIC SKILL
```

A Mega Skill is therefore **not** a flat router over prose stages. It is the apex representation of a complete real capability built from recursively composable Skill building blocks.

## Skill kinds

### 1. Atomic Skill

An **Atomic Skill** is the smallest maintained, independently useful procedure. It lives under `skills/<skill-id>/`, includes `SKILL.md`, and owns a trigger/use condition, input contract, method, output contract, source identity, and local validation.

### 2. Compound Skill

A **Compound Skill** is a proper reusable Skill implemented as a bounded composition of lower Skills. Existing `combo-skills/<combo-id>/COMBO.md` manifests remain the canonical compatibility/source representation for this class.

A Compound Skill may contain:

- Atomic Skills (`kind: skill`);
- other Compound Skills (`kind: compound-skill`);
- explicitly typed external capability references (`kind: external-skill`).

A Compound Skill owns its selection condition, ordered execution contract, member roles, handoffs, compound artifact, quality gates, state updates, and independent acceptance criteria. It does not copy child implementation.

Recursive Compound-Skill composition must form a **directed acyclic graph (DAG)**. Self-reference and direct or indirect composition cycles are invalid.

### 3. Mega Skill

A **Mega Skill** is a proper end-to-end Skill at mission scale. It is the apex of a hierarchy of Compound and Atomic Skills and owns the complete workflow/pipeline contract: mission trigger, route selection, durable state, phase gates, cross-branch integration, recovery, final acceptance, and mission output.

A Mega Skill is valid only when its full recursive dependency graph resolves to real Skill identities or explicitly typed external Skill references, every intermediate Compound node is independently valid as a Skill, and the graph is cycle-free.

## Dependency and identity law

```text
Atomic Skill ──┐
               ├──► Compound Skill ──┐
Compound Skill ┘                     ├──► Compound Skill ... ──► Mega Skill
Atomic Skill ────────────────────────┘
```

Composition moves toward greater integrated capability. A child Skill never depends on a parent merely to remain valid.

Exact human Skill IDs are preserved. Because an ID may exist in more than one layer, machine projections use a typed key:

```text
atomic:<id>
compound:<id>
mega:<id>
external:<id>
```

Typed keys prevent accidental identity collapse while preserving the exact canonical Skill ID.

Shared Skills may feed multiple parents or multiple Mega Skills. Therefore the canonical machine representation is a DAG even when a human-facing view is rendered as a pyramid.

## Recursive composition invariants

1. **Real-node invariant.** Every GlacierEQ-owned node resolves to a canonical registry entry and source path.
2. **Proper-Skill invariant.** Atomic, Compound, and Mega nodes each own a trigger/use condition, input/output or handoff contract, artifact contract, and validation boundary appropriate to scale.
3. **Recursive-composition invariant.** A Compound Skill may consume another Compound Skill by exact ID when the child independently satisfies the Compound-Skill contract.
4. **Acyclicity invariant.** Compound-Skill composition may never create a direct or indirect cycle.
5. **No-copy invariant.** Parents reference child Skill IDs, roles, contracts, and artifacts; they do not duplicate child methods.
6. **Compounding invariant.** Every parent adds integration capability that no child owns alone.
7. **Artifact invariant.** Every composition edge has a meaningful member role/handoff and every composite Skill emits a traceable artifact.
8. **Validation invariant.** A Mega Skill cannot be active if any required owned descendant is unresolved, invalid, or cyclic.
9. **Provenance invariant.** Source identity and lower-layer evidence survive every composition step.
10. **Shared-lineage invariant.** Reused nodes retain all parent/path lineage rather than being flattened into one occurrence.
11. **Context invariant.** Higher scale does not authorize unrelated context loading or silent scope expansion.

## Canonical recursive projection

`registry/mega-skill-pyramids.json` is a generated projection from the canonical registries:

```bash
python scripts/generate_mega_skill_pyramids.py
python scripts/generate_mega_skill_pyramids.py --check
```

`schema/mega-skill-pyramid.schema.json` defines the generated projection contract.

The projection contains:

- a typed `node_catalog` with the real source identity, artifact contract, maturity, and validation boundary of every node used by a Mega Skill;
- one graph entry for each Mega apex;
- recursive `node_refs` with all observed depths;
- typed edges preserving required/conditional status, member roles, produced artifacts, and execution validation;
- per-Mega shared-node lineage with all parent keys and root paths;
- global shared-node lineage showing reuse across Mega Skills;
- zero unresolved owned references and zero Compound-Skill cycles as generation preconditions.

There is no fixed maximum layer count. Level 0 is the Mega apex; descendants continue recursively until Atomic or explicit external leaves are reached.

The projection is generated, never hand-maintained. Canonical ownership remains in `skills.json`, `combo-skills.json`, `mega-skills.json`, and `external-skills.json`.

## Snowball acceptance test

| Test | Atomic Skill | Compound Skill | Mega Skill |
|---|---|---|---|
| Proper Skill identity | Required | Required | Required |
| Trigger/use condition | Required | Required | Required at mission scope |
| Input/output or handoff contract | Required | Required | Required |
| Reuses child IDs without copying methods | N/A | Required | Required |
| May recursively compose Compound Skills | N/A | Yes, cycle-free | Through descendants |
| Adds new value | Procedure | Composition + handoff | End-to-end integration + durable mission state |
| Traceable artifact | Atomic artifact | Compound artifact | Mission result + durable handoff |
| Independent validation | Required | Required | Required |
| Source/provenance preservation | Required | Required | Required |

If a proposed node cannot pass the appropriate acceptance test, it is not promoted merely because a document names it a Skill.

## Snowball cycle

```text
verified Atomic Skill artifact
        ↓
proper Compound Skill + explicit handoffs
        ↓
verified compound workflow artifact
        ↓
optional further Compound Skill composition
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
Compound Skill artifact (optional recursive levels)
        ↓ additive integration
Mega Skill mission state
```

A Compound or Mega Skill may compact, route, rank, annotate, or supersede an analysis artifact, but it may not silently rewrite the underlying source. If a later layer discovers an error, preserve the old artifact/proposition and record the correction, evidence, and effective supersession explicitly.
