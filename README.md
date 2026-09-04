# GlacierEQ Mega Skills

Mega-Skills is the canonical capability repository for building complete workflows and pipelines as **hierarchies of real Skills**.

```text
                                 MEGA SKILL
                         complete workflow / pipeline
                         /          |           \
              COMPOUND SKILL   COMPOUND SKILL   COMPOUND SKILL
                /      \              |             /       \
        ATOMIC SKILL   COMPOUND SKILL  ...     ATOMIC SKILL  ...
```

**Every building block is a proper Skill.** Atomic Skills own precise procedures. Compound Skills are independently valid reusable workflow Skills with ordering, handoffs, artifacts, and validation. Mega Skills are proper mission-scale Skills whose dependency pyramid forms the complete end-to-end workflow/pipeline.

Existing `combo-skills/` manifests remain canonical and supported; their semantic role is explicit: they are Compound-Skill source manifests, not non-Skill orchestration glue.

## Current registries

| Registry | Role | Current entries |
|---|---|---:|
| `registry/skills.json` | Atomic Skills | 709 |
| `registry/combo-skills.json` | Compound workflow Skills | 33 |
| `registry/mega-skills.json` | Mega apex Skills | 29 |
| `registry/mega-skill-pyramids.json` | Generated normalized recursive graph | 29 Mega roots |

Counts describe repository objects, not production/adoption claims.

## Recursive composition

Compound Skills may contain Atomic Skills, other validated Compound Skills, and explicit external references. Composition is a DAG: self-reference, direct/indirect cycles, and unresolved owned references fail validation.

Exact IDs are preserved. Typed machine keys (`atomic:`, `compound:`, `mega:`, `external:`) prevent cross-layer identity collisions while retaining the canonical human Skill ID. Shared Skills remain shared rather than being copied into each parent.

See [`HIERARCHY.md`](HIERARCHY.md) for the governing contract.

## Generate or verify the canonical graph

```bash
python scripts/validate_hierarchy.py
python scripts/generate_mega_skill_pyramids.py
python scripts/generate_mega_skill_pyramids.py --check
python tests/test_recursive_skill_hierarchy.py -v
```

The generated registry stores 29 Mega roots, canonical Compound adjacency, typed leaves, shared-node lineage, and canonical artifact/validation field paths. Any Mega pyramid can therefore be expanded deterministically to real Skill nodes without duplicating the underlying Skill contracts.

## Public projection

Job Application Helix projects a recruiter-facing view at:

`https://casey-barton-glaciereq.vercel.app/mega-skills/`

That site is a projection only. Canonical Skill identity, composition, validation, and provenance remain here.
