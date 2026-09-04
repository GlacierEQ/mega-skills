# GlacierEQ Mega Skills

**GlacierEQ Mega Skills** is the canonical private capability repository for building complete AI workflows and pipelines as **hierarchies of real Skills**.

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

The central rule is simple: **every building block in the pyramid is a proper Skill.** Atomic Skills own precise procedures. Compound Skills (represented by the existing Combo Skill manifests) are proper reusable Skills that own ordering, handoffs, and a compound artifact. Mega Skills are proper mission-scale Skills whose complete dependency pyramid forms an end-to-end workflow or pipeline.

The repository does **not** create capability by flattening instructions into a giant prompt. It composes validated Skill identities and artifacts.

> **Snowball rule:** every higher Skill consumes verified artifacts/contracts from lower Skills, adds new integration capability, and emits a more complete decision-ready artifact. Nothing gets bigger merely by repeating instructions.

## Current canonical registries

| Registry | Role | Current entries |
|---|---|---:|
| `registry/skills.json` | Atomic Skills | 709 |
| `registry/combo-skills.json` | Compound workflow Skills / compatibility manifests | 33 |
| `registry/mega-skills.json` | Mega apex Skills | 29 |
| `registry/mega-skill-pyramids.json` | Generated recursive Skill DAG/pyramid projection | 29 pyramids |

Counts are repository object counts, not production/adoption claims.

## Canonical ontology

See [`HIERARCHY.md`](HIERARCHY.md).

- **Atomic Skill** — independently useful procedure with inputs, outputs, method, artifact, and local validation.
- **Compound Skill** — independently selectable reusable workflow Skill composed from Atomic, recursive Compound, and/or explicit external Skills, with ordered handoffs, a compound artifact, and independent validation.
- **Mega Skill** — mission-scale Skill whose apex integrates multiple Compound/Atomic Skills into a complete recoverable workflow/pipeline.

Existing `combo-skills/` manifests remain supported; their semantic role is now explicit: they are the source manifests for **Compound Skills**, not non-Skill orchestration glue.

## Machine-readable pyramids

Generate or verify the full hierarchy projection:

```bash
python scripts/generate_mega_skill_pyramids.py
python scripts/generate_mega_skill_pyramids.py --check
```

The generated registry recursively resolves every Mega apex until Atomic or explicit external leaves are reached. It refuses unresolved owned references and Compound-Skill cycles. Exact IDs are preserved, while typed machine keys (`atomic:`, `compound:`, `mega:`, `external:`) prevent cross-layer identity collisions. Shared lower Skills retain all parent/path lineage; the machine form is therefore a DAG even though the human form is rendered as a pyramid.

## Quality gate

Run before merge:

```bash
python scripts/validate_hierarchy.py
python scripts/generate_mega_skill_pyramids.py --check
python -m unittest discover -s tests -v
git diff --check
```

## Public projection

The recruiter-facing/public explanation is projected through Job Application Helix at:

`https://casey-barton-glaciereq.vercel.app/mega-skills/`

The public surface is a projection only. Canonical Skill identities, composition, validation, and provenance remain in this repository.
