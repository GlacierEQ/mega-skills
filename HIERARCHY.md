# Capability Hierarchy and Recursive Mega-Skill Pyramid Contract

## Prime ontology

**Every node in a Mega-Skill pyramid is a proper Skill.** Atomic, Compound, and Mega are scale/composition kinds, not different standards of legitimacy.

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

A Mega Skill is the apex representation of a complete real capability built from recursively composable Skill building blocks. It is not a flat router over prose stages.

## Skill kinds

### Atomic Skill

An independently useful procedure with a complete trigger, input contract, method, output contract, artifact, source identity, and local validation. Atomic means independently composable, not capability-starved or architecturally trivial.

### Compound Skill

A proper reusable Skill implemented as a bounded composition. Existing `combo-skills/<id>/COMBO.md` manifests are the canonical compatibility/source representation for this class.

A Compound Skill may contain Atomic Skills (`kind: skill`), other Compound Skills (`kind: compound-skill`), or explicit external capability references (`kind: external-skill`). It owns selection conditions, ordered execution, member roles, handoffs, a compound artifact, quality gates, state updates, and independent acceptance criteria.

Recursive Compound-Skill composition must form a directed acyclic graph. Direct or indirect cycles and unresolved owned references are invalid.

### Mega Skill

A proper end-to-end Skill at mission scale. It owns mission trigger, route selection, durable state, phase gates, cross-branch integration, recovery, final acceptance, and mission output. Its full dependency graph must recursively resolve to valid Compound/Atomic Skills or explicit external leaves.

## Identity law

Exact human IDs are preserved. Machine projections use typed keys because an exact ID may legitimately exist at more than one Skill scale:

```text
atomic:<id>
compound:<id>
mega:<id>
external:<id>
```

Shared Skills may feed multiple parents or multiple Mega Skills, so the canonical machine form is a DAG even when a human view is rendered as a pyramid.

## Recursive invariants

1. Every GlacierEQ-owned node resolves to a canonical registry entry and source path.
2. Every Atomic, Compound, and Mega node is independently valid at its scale.
3. A Compound Skill may consume another validated Compound Skill by exact ID.
4. Composition is acyclic; cycle introduction fails validation.
5. Parents reference child IDs/contracts/artifacts and never copy child methods.
6. Every parent adds integration capability no child owns alone.
7. Member roles, handoffs, produced artifacts, and validation boundaries remain attributable to their canonical contracts.
8. Required unresolved descendants block Mega validity.
9. Source/provenance survives composition.
10. Shared-node lineage is preserved instead of flattened.
11. Higher scale does not authorize unrelated scope/context loading.

## Canonical graph projection

`registry/mega-skill-pyramids.json` is generated from the canonical registries. It is normalized so shared Skills are represented once and referenced by typed key.

It contains:

- `mega_roots`: all 29 Mega apexes and their required/conditional Compound roots;
- `compound_nodes`: every Compound Skill and typed child references with exact child roles;
- `leaf_keys`: Atomic/external leaves reachable from Compound Skills;
- `shared_node_lineage`: nodes with multiple parents;
- `contract_paths`: exact canonical registry fields carrying artifact and validation semantics;
- `expansion_contract`: deterministic recursive traversal rules.

Generate/check it with:

```bash
python scripts/generate_mega_skill_pyramids.py
python scripts/generate_mega_skill_pyramids.py --check
```

There is no fixed maximum composition depth. Expansion starts at a Mega root, recursively follows `compound-skill` members, and stops only at Atomic or explicit external leaves.

## Snowball acceptance

A higher Skill must consume real lower-Skill contracts/artifacts, add new integration value, emit a traceable artifact, and remain independently testable. Nothing becomes a Mega Skill merely by collecting prompts or repeating instructions.

## Source preservation

```text
source/evidence
  ↓ immutable provenance
Atomic Skill artifact
  ↓ additive composition
Compound Skill artifact
  ↓ optional recursive Compound layers
Mega Skill mission result + durable state
```

Higher Skills may route, compact, annotate, or supersede analysis artifacts, but may not silently rewrite the underlying source or erase supersession lineage.
