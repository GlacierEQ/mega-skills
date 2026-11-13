# Evidence capability selector — mesh handoff

Repository: GlacierEQ/mega-skills
Documentation revision: 1
Evidence: `ops/receipts/evidence-capability-selector.json`
Implementation commit: b99dad2a239ffcc3a06b1665cc480a501c931d60

## Ownership

One writer for this change: `scripts/evidence_capability_selector.py` and `tests/test_evidence_capability_selector.py`.

Do not edit `capability_runtime.py` or `OMP_POWER_SELECTION` in the same change. Those are the baselines.

## Concurrency

No worktree split was required. The change is additive and does not share write scope with the open draft activation PRs (#56, #55, #54, #53, #47, #24).

## Handoff object

`select_evidence_aware(... )["omp_selection"]` is the only handoff to an installer:

```text
{"atomic": [...], "compound": [...], "mega": [...]}
```

A coordinator may pass that object as `selection` to `sync_omp_skills` in preview mode (`apply=False`). An `apply=True` call is a separate authorized action and is not part of this module.

## Conflict rule

If a lexical baseline and this selector disagree, keep both outputs in the receipt. Do not silently replace the fixed coalition default.

## Integration

Merge of this branch is not authorized by the module. Main stays on the pre-existing coalition until a merge is explicitly requested.
