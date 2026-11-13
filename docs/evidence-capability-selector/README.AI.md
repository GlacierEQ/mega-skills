# Evidence capability selector — agent contract

Repository: GlacierEQ/mega-skills
Documentation revision: 1
Evidence: `ops/receipts/evidence-capability-selector.json`

## Source map

- Selector: `scripts/evidence_capability_selector.py`
- Untouched lexical baseline: `scripts/capability_runtime.py`
- Untouched installer and fixed coalition: `scripts/sync_runtime_skills.py` (`OMP_POWER_SELECTION`, `sync_omp_skills`)
- Assay producer: `scripts/readiness_assay.py`
- Assay data: `registry/skill-readiness.json`
- Tests: `tests/test_evidence_capability_selector.py`
- Docs: `docs/evidence-capability-selector/`

## Execute

```bash
python -m unittest tests.test_evidence_capability_selector -v
python scripts/evidence_capability_selector.py "QUERY" --limit 5
```

Working directory is the repository root. Tests build their own fixture and do not need the live registries.

## Constraints

- Do not load every skill body into an agent prompt because a selector returned ids.
- Do not call `sync_omp_skills(..., apply=True)` from this module. It has no apply path.
- Do not change `STATE_BENEFIT`, `ACTIVATION_FLOOR`, or `LEXICAL_CAP` to improve a number you already saw. Record a new experiment instead.
- Do not mark `activation_performed` true. The field exists so a caller cannot confuse a ranking with an install.
- Missing `registry/skill-readiness.json` must keep failing closed.
- `purpose` is still ignored by candidate generation. Fixing that is a different change and would invalidate the "same pool" comparison.
- Owning Linear issue for the prior activation work is HI-826. Do not open a new issue for this selector unless the operator asks.

## Recovery

If selection looks wrong, compare the three lists from `compare_tasks`: lexical ids, evidence ids, coalition ids. The receipt's live task dump is the reference run against main `fa5e5efe8993c52e7095d1d118ad3a735b2381f9`.
