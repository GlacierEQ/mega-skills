# Evidence capability selector — specialist note

Repository: GlacierEQ/mega-skills
Module: `scripts/evidence_capability_selector.py`
Baseline preserved: `scripts/capability_runtime.py` (unchanged), `OMP_POWER_SELECTION` in `scripts/sync_runtime_skills.py` (unchanged)
Documentation revision: 1
Evidence: `ops/receipts/evidence-capability-selector.json`
Canonical commit: b99dad2a239ffcc3a06b1665cc480a501c931d60

## Problem

`sync_all()` links every atomic skill directory into legacy runtimes. `sync_omp_skills()` defaults to a fixed 30-skill coalition, explicitly not a task selector. `resolve_capabilities()` ranks by identifier/description token overlap and does not read `registry/skill-readiness.json`.

SWE-Skills-Bench's relevant result for this repo: injecting more skills is not a quality strategy. Selection has to show a benefit on a fixed task list.

## Mechanism

1. Call `resolve_capabilities(root, query, limit=100)` for the candidate pool.
2. Join each packet to the assay on `(layer, id)` where atomic↔skill, combo↔combo, mega↔mega.
3. Score with locked constants in the module: `STATE_BENEFIT`, `LEXICAL_CAP = 30`, `ACTIVATION_FLOOR = 50`.
4. Hard-exclude, unless the query is the exact skill id: missing assay row, `implementation_missing`, `contract_incomplete`, `implementation_partial`, and (via the floor) `implementation_unverified`.
5. If `skills/` exists, a missing `contract_ref` hard-excludes non-exact rows.
6. Emit at most `limit` rows (1–30) plus `omp_selection` shaped `{atomic, compound, mega}`.

`implementation_unverified` is not in the hard-exclude set; its benefit (8) plus capped lexical (30), version (5), and the active-but-not-ready penalty (−25) stays under the floor.

Exact-id queries still return a below-floor skill and set `operator_exact_override`.

## Tracks considered

| Track | Mechanism | Result |
|---|---|---|
| A | Fixed `OMP_POWER_SELECTION` (30) and uncapped lexical top-k | Preserved as baselines |
| B | Re-rank the same lexical pool with assay state, source flags, semver presence, maturity conflict | Shipped. Fixture tests require a gold-hit tie-or-better vs lexical, a strict forbidden-injection drop, and a smaller set than the coalition |
| C | Embedding or whole-catalog retrieval | Not built. No experiment, no operational claim |

## Security and failure

- Read-only. No subprocess, no network, no credential read.
- Missing assay raises `EvidenceUnavailable` instead of activating the lexical list.
- Installer, profile writes, and rollback stay in `sync_omp_skills`. To roll back a caller's use of `omp_selection`, stop passing it. The default coalition is intact.
- Do not treat registry `maturity: active` as evidence. The scorer penalizes active entries the assay marks not ready.

## What was measured on 2026-11-13

Ten queries fixed from recovered ids before the run. Weights were not changed after the run.

- Evidence gold hits 10/10, lexical 10/10, fixed coalition 4/10.
- Forbidden unverified injections: evidence 0, lexical 2 (`diagnosing-bugs`, `story-lifecycle`), coalition 0.
- Mean selected: evidence 4.2, lexical 4.3, coalition 30.
- Top-1 displacement: evidence ranked `re-reconstruction-verification` ahead of `verification-before-completion`, and `mega-skills-test-runner` ahead of `test-driven-development`, because those leaders are `behavior_verified` and the specific skills are `instruction_ready`. Both specific skills stayed inside k=5.

This does not prove a SWE-bench or agent pass-rate lift.

## Operations

Regenerate the assay with the existing tool before trusting a selection on a dirty tree:

```bash
python scripts/readiness_assay.py --pass 2
```

That command rewrites registries when `--apply` is added. The selector never passes `--apply`.
