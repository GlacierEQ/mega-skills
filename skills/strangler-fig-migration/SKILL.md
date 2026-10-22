---
name: strangler-fig-migration
description: "Replace a legacy subsystem incrementally behind a facade (strangler fig pattern, Martin Fowler): route usage slice by slice to the new implementation and delete the old only when the new carries everything."
---

# Strangler Fig Migration

Modernize legacy subsystems without a big-bang rewrite: place a facade in front of the old system, grow the replacement behind it slice by slice, and retire the old system only on proven zero traffic.

## Workflow

1. Identify the seam and intercept it with a facade that initially routes 100% to the old implementation.
2. Pin current behavior with characterization-tests-first on the slices to be moved.
3. Implement the replacement for slice one behind the facade; route it; verify parity under real usage.
4. Repeat per slice, in risk order, recording routing evidence per slice.
5. When routing shows zero usage of the old implementation, retire it via deprecation-removal and delete the facade if it no longer earns its place.
6. Emit the migration record: slices, routing evidence, parity results, retirement receipt.

## The pattern

**Provenance:** published pattern — Martin Fowler, *Strangler Fig Application* (martinfowler.com/bliki). Registered as knowledge with attribution; no code is lifted.

Named for the strangler fig that grows around a host tree until the host is gone:

1. **Intercept.** Put a facade/proxy at the seam — the one place all consumers pass through. If no seam exists, creating it is step zero.
2. **Slice.** Move one coherent usage slice (a route, a feature, a data flow) to the new implementation behind the facade. Slices are ordered by risk: read-only and low-traffic first.
3. **Prove per slice.** Each slice carries its own verification (characterization tests on the old behavior, parity checks on the new). Traffic share is measured, not assumed.
4. **Retire on zero.** The old implementation is deleted only when routing evidence shows it carries nothing. Deletion follows deprecation-removal discipline.

## Safety gates

- Never delete the old implementation on schedule — only on zero-traffic evidence.
- The facade is a seam, not a new permanent layer; plan its own removal or justify its keep.
- Every slice must be independently reversible at the facade (route back) until retirement.

## Output contract

- Facade with per-slice routing and traffic evidence
- Retirement receipt when the old system reaches zero routed usage

## Related skills

- branch-by-abstraction — the in-codebase sibling pattern when no facade seam exists
- characterization-tests-first — pins behavior before slices move
- deprecation-removal — runs the final retirement
- legacy-estate — operating rules for the legacy repos this pattern modernizes

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/strangler-fig-migration/tests -v
git diff --check
```
