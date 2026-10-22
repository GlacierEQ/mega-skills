---
name: test-drift-archaeology-repair
description: "Repair a test suite that rotted against a refactor: enumerate the full failure set, find the causing refactor by git archaeology, restore what consumers still need, merge forked shapes instead of picking winners, add the missing surface tests specify, and return the suite to green without weakening a single test."
---

# Test Drift Archaeology Repair

Own the estate's proven drift-repair pattern (executed 2026-10-14 on Casebuilder4000, apex-control-plane, operator-administration): restore a rotted suite to fully green by repairing the code/test mismatch at its archaeological root, never by weakening tests.

## Workflow

1. Run the full suite; record the exact error/failure counts and the failing module list. This is the denominator.
2. Cluster failures by signature; identify the refactor commit(s) that introduced the drift via git log/blame on the implicated modules.
3. For each cluster decide the repair direction from evidence: restore dropped definitions, merge forked shapes, add missing surface, or fix a genuine code bug the drift exposed.
4. Apply repairs cluster by cluster, re-running the affected tests after each; never let a repair silently change behavior outside the drift.
5. Run the full suite to green and the project's demo/build path end-to-end.
6. Commit to main with the archaeology in the message: what drifted, what caused it, what was restored/merged/added, final counts.

## The pattern, as executed

**Provenance:** `GlacierEQ/Casebuilder4000` commit `46cde78` (suite 185/185 green after 21 errors + 49 failures); same-day applications: `apex-control-plane` `803593d`, `operator-administration` `2e7bd92` + `27d16e5`. This skill registers that executed pattern as the estate's default recovery method.

- **Enumerate first.** Run the *whole* suite and count errors vs failures before touching anything. A repair scoped from a sample is scoped wrong.
- **Archaeology.** Use git history and call sites to find the refactor that caused the drift (in the provenance case, a refactor dropped 9 model names that 8+ modules still required). The question is never "which test is wrong" first — it is "what changed underneath".
- **Restore and merge.** Reconstruct dropped definitions from their call sites. When two layers forked a shared shape, **merge the shapes so both field sets coexist** — do not pick a winner and break the other consumer.
- **Add the missing surface.** When tests specify surface the code lacks (CLI commands, enum members), add the surface; do not edit the tests down to the code.
- **Normalize at boundaries.** Vocabulary mismatches are fixed at the boundary layer (e.g. engine term → kernel term in the kernel module), not by renaming across the codebase.

## Safety gates

- Never delete, skip, or weaken a test to reach green — the suite is the specification of what consumers need.
- Never repair from a sampled subset; the full enumeration is the scope.
- If archaeology shows the *tests* encode a deliberately removed behavior, stop and surface it — that is a decision, not drift.

## Output contract

- Fully green suite with the drift root cause named
- Repair commit(s) to main with the archaeology recorded in the message

## Related skills

- test-fixing — systematic failure fixing for ordinary breakage (this skill is for refactor-induced rot)
- systematic-debugging — root-cause discipline shared by both
- verification-before-completion — green claims require full-suite output
- ast-repair-core — AST-level repair tooling usable inside a cluster fix

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/test-drift-archaeology-repair/tests -v
git diff --check
```
