---
name: branch-by-abstraction
description: "Upgrade or replace a widely-used dependency or subsystem without long-lived branches: introduce an abstraction seam, run old and new behind it, flip by configuration, then remove the old. Matches the estate's no-branches rule."
---

# Branch By Abstraction

Make large in-place replacements safely inside one codebase on main: an abstraction layer decouples consumers from the implementation being replaced, so the swap happens as a sequence of small, verified, reversible steps.

## Workflow

1. Map the consumer surface of the component being replaced; design the thinnest abstraction that covers it.
2. Migrate consumers onto the abstraction with the old implementation behind it; full suite green at each step, all on main.
3. Implement the replacement behind the abstraction; test it against the abstraction's contract (characterization tests).
4. Flip by configuration in the safest environment first; observe; widen.
5. Remove the old implementation; simplify or remove the abstraction if it is now ceremony.
6. Emit the swap record: seam design, flip points, verification results, removal receipt.

## The pattern

**Provenance:** published pattern — Paul Hammant's *Branch By Abstraction* (branchbyabstraction.com), in the Fowler lineage. Registered as knowledge with attribution; no code is lifted.

Five moves:

1. **Abstract.** Introduce an abstraction layer between consumers and the current implementation; migrate consumers to call the abstraction (behavior unchanged).
2. **Implement behind.** Build the new implementation against the same abstraction, unused.
3. **Flip.** Switch implementations by configuration/flag — per environment, per consumer group if needed. Both implementations remain runnable.
4. **Verify in place.** The flipped system runs under real usage with the old implementation one flag-flip away.
5. **Remove.** Delete the old implementation and, if it no longer earns its keep, the abstraction.

The pattern exists precisely for estates that do not use long-lived branches: the "branch" is the abstraction, and it lives on main.

## Safety gates

- Never flip globally first — the flip order is safest-scope to widest, with rollback a config change.
- The abstraction must be thinner than the problem; a seam that grows its own logic becomes the next legacy component.
- Old implementation stays runnable until the flip has survived real usage, not just tests.

## Output contract

- Abstraction seam with old and new implementations behind it
- Flip record and old-implementation removal receipt

## Related skills

- strangler-fig-migration — the cross-seam sibling pattern
- characterization-tests-first — the contract evidence for both implementations
- deprecation-removal — the discipline for the final old-code deletion
- fleet-git-harmonizer-core — main-as-baseline discipline this pattern depends on

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/branch-by-abstraction/tests -v
git diff --check
```
