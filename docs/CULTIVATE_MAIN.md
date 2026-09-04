# Cultivate Main

`main` is a living line. It is grown by harvesting unique value from
branches and pull requests. It is never reset, force-pushed, renamed, or
replaced because another ref is newer or larger.

## Operator of record

The cultivate-main assessor is allowed to **finish** work that passes
its gates. Waiting on Casey is not a completion strategy.

Casey is required only for the Casey class:

- history rewrite
- force-push
- credential or secret-bearing history
- legal filing / privilege waiver
- production deploy of an external system
- deletion of protected refs
- replacing `main`

Everything else that is mergeable, additive, and free of those hazards
is an automatic merge-commit into `main`.

## Best-of-all-worlds law

1. Preserve useful divergence. Do not squash away unique commits when
   history is the evidence.
2. Integrate the stronger capability into `main`. Prefer a merge commit
   so both lines remain reconstructable.
3. If two branches solve the same problem, take the version that keeps
   tests, contracts, and unique behavior. Do not pick by age or size.
4. If a branch is behind, update it onto current `main` and reassess.
   Do not abandon it because it is stale.
5. Deny destructive action when evidence is incomplete.
6. Close the lifecycle after integration. Do not leave a finished
   workstream open as a second trunk.

## Decision classes

| Class | Meaning | Action |
|---|---|---|
| `AUTO_MERGE` | Additive, scoped, no Casey hazard, mergeable | Merge commit into `main` |
| `HARVEST` | Unique value plus conflict or missing check | Update branch, resolve, then merge |
| `PRESERVE` | Live independent workstream | Keep; do not delete |
| `REDUNDANT` | Already in `main` | Close PR; retire ref after proof |
| `CASEY` | Hazard class above | Packet only |

## Runner

```bash
python scripts/cultivate_main.py --report
python scripts/cultivate_main.py --apply --repo GlacierEQ/mega-skills
python tests/test_cultivate_main.py -v
```
