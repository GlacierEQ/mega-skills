# Evidence-aware capability selection

Repository: GlacierEQ/mega-skills
Module: `scripts/evidence_capability_selector.py`
Documentation revision: 1
Canonical commit: recorded in `ops/receipts/evidence-capability-selector.json` after the introducing commit
Evidence: `ops/receipts/evidence-capability-selector.json`

Select a small set of Mega-Skills for one task using the readiness assay. This does not install skills into OMP, Codex, or any other host.

## What you get

- The lexical resolver stays the candidate generator (`scripts/capability_runtime.py`).
- Assay state decides which of those candidates are safe to activate.
- Output includes an `omp_selection` object you can pass to `sync_omp_skills(..., selection=)` after a separate preview. This tool never calls that installer.

## Quick start

From a checkout of this repository:

```bash
python scripts/evidence_capability_selector.py "autonomous software engineering" --limit 5
python -m unittest tests.test_evidence_capability_selector -v
```

Compare a fixed task list:

```bash
python scripts/evidence_capability_selector.py --compare tasks.json --limit 5
```

`tasks.json` is a list of `{ "id", "query", "relevant", "forbidden_ids" }`.

## Requirements

- Python 3.10+
- `registry/skills.json`, `registry/combo-skills.json`, `registry/mega-skills.json`
- `registry/skill-readiness.json` produced by `scripts/readiness_assay.py`

No network, credentials, or extra packages.

## Limitations

- Not a host activation. `activation_performed` is always false.
- Not a coding-benchmark pass-rate result. The measured comparison is gold-hit, unverified injection, and selection count on registry metadata.
- Lexical scores are capped at 30 inside the evidence score, so a loosely related `behavior_verified` skill can rank above a more specific `instruction_ready` skill. On the 2026-11-13 live run this happened for "verification before completion" and "test driven development"; the specific skill remained inside the top 5.
- The baseline resolver does not score the `purpose` field. This selector does not widen the candidate pool to compensate.
- Almost every registry version is `0.1.0`, so the semver check does not currently change ordering.
- Source-file existence is enforced only when `skills/` is present in the checkout.
- The fixed OMP coalition is unchanged. Passing a custom selection is a caller decision.
