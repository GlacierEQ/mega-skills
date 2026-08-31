---
name: local-skill
description: Meta-skill that inspects the mega-skills repository, extracts structural and behavioral patterns from existing skills, and generates complete, ready-to-commit new skills (or mega-skills) on demand. Use when asked to create, scaffold, or bootstrap any new skill that must conform to the GlacierEQ mega-skills conventions.
---

# Local Skill

## Use this skill when

Use this skill whenever a new skill (or mega-skill) must be created that matches the living conventions of the `GlacierEQ/mega-skills` repository. It is the local, repository-aware counterpart to external skill-creation flows: it reads the actual tree, SKILL.md front-matter, skill.py dispatchers, scripts/, resources/, tests/, __init__.py, and requirements.txt patterns, then emits a complete directory ready for commit.

Do **not** use this skill for one-off scripts or non-skill Python packages. Use it only when the output must be a first-class citizen under `skills/<name>/`.

## Decision gate

Proceed only when:

1. The target skill name is a valid hyphenated identifier that does not already exist (or an explicit overwrite/migration is authorized).
2. At least one existing skill can serve as a structural exemplar (default: `mega-skill-forge` or the closest semantic match).
3. The requested capability can be expressed as a bounded set of scripts + resources + tests rather than an unbounded conversation.
4. The generated artifacts will include a valid SKILL.md front-matter block, executable skill.py entrypoint, and at least one focused test.

If any condition fails, emit a missing-precondition report and stop.

## Creation workflow

1. **Inspect the living repo.** Walk `skills/`, sample representative SKILL.md, skill.py, scripts/, resources/, tests/, and requirements.txt files. Record the current default-branch SHA and the dominant structural patterns.
2. **Resolve the exemplar.** Select the closest existing skill (or force `mega-skill-forge` for true meta/mega work). Extract its dispatcher pattern, script naming, resource schema style, and test skeleton.
3. **Draft the contract.** Write the new skill’s SKILL.md with correct front-matter (`name`, `description`), decision gate, workflow, and resource table. Mirror the prose density and section order of high-quality exemplars.
4. **Generate the implementation surface.**
   - `skill.py` — thin dispatcher that maps CLI commands to scripts/.
   - `scripts/*.py` — one focused script per named operation (pattern extraction, generation, validation, etc.).
   - `resources/` — YAML config, JSON schema, any templates needed by the new skill.
   - `tests/test_<name>.py` — L2 structural + behavioral smoke tests.
   - `__init__.py` and `requirements.txt`.
5. **Validate hierarchy.** Confirm the generated tree is self-consistent, executable bits are set, and the new skill can be discovered by the same mechanisms that discover every other skill.
6. **Emit ready-to-commit.** Produce the full directory tree as files (or a single commit via the GitHub tools). Never leave partial scaffolds.

## Modification workflow

Treat an existing local-skill change as a compatibility change. Re-inspect the current mega-skills tree before altering generation templates. Preserve existing script names and resource keys unless an explicit migration is documented in the same change.

## Quality standard

A successful run of local-skill produces a skill that:

- Passes the same structural tests every other skill is expected to pass.
- Contains a non-empty, actionable SKILL.md that an operator can follow without reading the generator source.
- Ships at least one real script that does more than `print("hello")`.
- Leaves no temporary or partial files in the repository.

## Resources

| Resource | Use |
|---|---|
| `resources/local_skill_config.yaml` | Runtime toggles and default exemplar selection. |
| `resources/local_skill_schema.json` | JSON Schema for generation requests and output contracts. |
| `resources/SKILL.md.template` | Canonical front-matter + section skeleton. |
| `resources/skill.py.template` | Thin dispatcher template. |
| `references/pattern-catalog.md` | Living notes on observed conventions across the skills/ tree. |

## Commands

```
local-skill inspect          # walk skills/ and summarize patterns
local-skill extract <name>   # deep-extract one existing skill
local-skill generate <name>  # produce a complete new skill directory
local-skill validate <path>  # structural + convention checks
local-skill this-skill       # self-description / readiness
```
