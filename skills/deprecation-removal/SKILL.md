---
name: deprecation-removal
description: "Retire deprecated APIs, flags, and features completely: inventory every usage, migrate the consumers, delete the deprecated surface, and prove zero remaining references. Engines: Piranha for flags, OpenRewrite recipes for APIs."
---

# Deprecation Removal

Own the deprecation-retirement discipline end-to-end — the registry's second named gap: a deprecated surface is not retired when it is marked, but when consumers are migrated, the code is deleted, and absence is proven by search.

## Workflow

1. Record the retirement decision and rationale; name the replacement (or record that there is none).
2. Build the complete reference inventory by structural and textual search; classify every hit (consumer, test, doc, config, the surface itself).
3. Assign each consumer a disposition and migrate them in bounded batches with the engine skills.
4. Delete the deprecated surface; run the full build and suite.
5. Re-run the inventory search: zero live references is the completion condition. Record any exemptions with reasons and expiries.
6. Emit the retirement receipt: original inventory, dispositions, deletion diff, absence proof, exemptions register.

## Retirement is a sequence, not an annotation

Deprecations fail socially, not technically: the annotation lands, consumers never move, and the surface lives forever. This skill runs the full sequence.

1. **Inventory.** Every reference to the deprecated surface — code, config, docs, tests, flags — enumerated by search, not sampled. The inventory is the denominator for the whole retirement.
2. **Migrate consumers.** Each consumer gets a disposition: migrated to the replacement, deleted with the feature, or explicitly exempted with a reason and an expiry. Exemptions without expiry are how deprecations become permanent.
3. **Delete the surface.** Only when the inventory shows zero live consumers. Flags go through Piranha; APIs through OpenRewrite recipes or structural rewrites; hand deletion is the last resort, never the first.
4. **Prove absence.** The same search that built the inventory now returns zero. Absence is a command output, not an impression.

## Safety gates

- Never delete a surface with un-migrated live consumers — inventory before deletion, always.
- Never accept a permanent exemption; every exemption carries a reason and an expiry date.
- Deprecation annotations without an inventory and a retirement plan are forbidden output of this skill — they are how the problem starts.

## Output contract

- Consumer migration plan with per-consumer disposition
- Deletion diff plus zero-reference proof and retirement receipt

## Related skills

- piranha-flag-retirement — the flag-deletion engine
- openrewrite-recipes — the API-migration engine
- spiral-promotion-gate — promotes the replacement before the old surface is retired
- verification-before-completion — absence claims require command output

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/deprecation-removal/tests -v
git diff --check
```
