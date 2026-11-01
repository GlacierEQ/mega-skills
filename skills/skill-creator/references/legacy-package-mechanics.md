# Preserved upstream authoring mechanics

This reference preserves the technically valuable ideas from the prior `skills/skill-creator/SKILL.md`, which was an upstream-derived Claude skill-creation guide. The original 355-line body remains in the GlacierEQ/mega-skills Git history prior to `137a46132a321b634556782f5e217ee70f9b770c`; the repository `GlacierEQ/antigravity-awesome-skills/skills/skill-creator/` also retains its source and helper scripts. This document retains its mechanics without pretending they are implemented in the current host.

## Loading budget and structure

A skill is a loadable package rooted in `SKILL.md` with YAML frontmatter `name` and `description`. Additional host keys (`license`, `allowed-tools`, metadata) are host dependent and must be confirmed against that host's validator. The **description** determines candidate discovery and should state both what the skill does and when it is selected. The body is loaded only after selection. Scripts and references should provide reusable depth, not consume the entire context window at once. Keep references reachable directly from the body and avoid deep nesting. `assets/` contains output ingredients, not instructions.

Degree of freedom is set by the fragility of the task: prose heuristics for flexible judgment, parameterized pseudocode/scripts for constrained variation, and deterministic scripts for safety-sensitive or error-prone operations. Match precision to failure costs; don't issue a universal template to all domains.

## Existing upstream helper lineage

The antigravity copy contains `scripts/init_skill.py`, `scripts/quick_validate.py`, and `scripts/package_skill.py`. The earlier mega-skills guide refers to these names, but only their *presence in the original upstream repository* was independently recovered; do not assume these executable helpers exist in another host or at the same path. Verify source, dependencies and execution environment before using them. The mega-skills owned `scripts/validate_package.py` is a separate, stdlib-only defensive preflight with static-only result semantics, not a semantic evaluator or upstream loader replacement.

If the host's native packager is available, validate against that host, then run the owned preflight and a relevant behavioral evaluation. Where no host packager is available, the new owned `--package` path can produce an archive after static validation. ZIP creation, Python importability, host installation, selection, behavioral routing, and live provider execution are distinct evidence stages.

## Lifecycle details worth keeping

1. Elicit concrete triggering and non-triggering examples using actual user workflows or validated scenarios.
2. Determine reusable references/scripts/assets from repeated decisions and common errors rather than automatic boilerplate.
3. Initialize a new package only when no strong owner exists; for an existing skill, improve in place.
4. Add and test executable resources against realistic fixtures, including malicious inputs, bad paths, and missing dependencies.
5. Test loader metadata, trigger boundaries, package security, skill behavior, handoffs, and consumer activation separately.
6. Package and version after source/readback; record hashes and explicit verification states.
7. Iterate from observed failures rather than editing descriptions to inflate a score.

The existing source also cautions against unnecessary READMEs, changelogs, and unrelated files inside skill packages. Retain that hygiene while keeping genuinely necessary quality resources such as `tests/` and decision-focused references. Preserve licenses and provenance of any copied third-party code or text.