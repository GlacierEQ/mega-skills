---
name: re-version-comparison
description: "Differential reverse engineering with REA: artifact, function, and bundle comparisons across versions; changed-behavior discovery; call-path construction; and static/runtime correlation — with comparison completeness rules that keep absence claims honest."
---

# RE Version Comparison

Own the differential lane. "What changed between versions" is where reverse engineering earns its keep — and where sloppy comparisons manufacture false absences. REA's comparison tools have strict completeness rules; this skill enforces them.

## The comparison tools

- `compare_artifacts` — compares inventory pages by occurrence path, content, metadata, and graph relations.
- `compare_functions` — compares explicit function Evidence. It is deliberately not a fuzzy whole-binary matcher: functions enter comparison as identified dossiers.
- `compare_bundles` — compares canonical bundle membership and unknown history.
- `find_changed_behavior` — combines existing comparisons into changed-behavior candidates.
- `build_call_path` — needs explicit function dossiers from one artifact/provider; an incomplete frontier makes absence **unknown**, never "no path exists."
- `correlate_static_and_runtime` — uses explicit mappings between static and runtime records; matching patterns are hypotheses, not causality.
- Native function matching supports the function-level work: matched procedures across builds carry their match evidence with them.

## Workflow

1. Produce comparable inputs first: both sides analyzed by the same family skill, at compatible detail. A summary-page comparison against a complete-record comparison is invalid — use complete, compatible page sets when claiming equivalence or absence.
2. Compare inventories before code: occurrence-level deltas (added/removed/changed paths, digests, graph relations) scope the deeper function comparison.
3. Compare functions from explicit dossiers; record match quality and the frontier actually covered.
4. Run `find_changed_behavior` over the comparisons and label every result: static difference = candidate. Only runtime corroboration (re-dynamic-analysis) promotes a candidate to an observed behavior change.
5. Keep `source_complete` separate from page exhaustion in every claim: a missing match in partial source Evidence does not establish absence.

## Safety gates

- Equivalence claims require the complete compatible sets; anything less is reported as "no difference found within the compared coverage" — the coverage named.
- Both sides' artifacts pass through re-safety-gate and re-untrusted-content-defense like any target.

## Output contract

- Comparison Evidence record with coverage sets named
- Changed-behavior candidates with evidence class per item

## Related skills

- re-evidence-record — completeness and absence discipline
- re-dynamic-analysis — runtime corroboration for candidates
- re-reconstruction-verification — verified deltas feed reconstruction specs

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-version-comparison/tests -v
git diff --check
```
