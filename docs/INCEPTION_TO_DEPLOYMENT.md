# Inception-to-Deployment Deep-Work Pipelines

Mega Skills describe complete workflows. These pipelines make that description **executable** while preserving source integrity, provider constraints, and scoped consequence boundaries.

## Span

```text
inception → readiness → recon → design → build
        → verify → package → execute/deploy → readback → evolve
```

Every family pipeline covers the same span. The master pipeline `inception-to-deployment` is the graph that may claim the full product loop when the requested target state is actually verified.

## Execution rule

There is no terminal `READY_PENDING_HUMAN_APPROVAL` permission gate.

Pipelines may, under active Operator mission authority:

- validate hierarchy and Combo/Mega contracts;
- run tests and repair failures;
- write run artifacts and receipts;
- mutate exact-target repositories/services through verified routes;
- merge or deploy when that action is part of the current mission and provider permissions allow it;
- read back the target state and persist receipts.

A new scoped authority decision is required only when execution would introduce a **new major strategy**, destructive/irreversible act, credential or permission administration, or external consequence not already covered by current Operator direction.

Missing optional providers, unrelated test surfaces, or a local route failure do not create a global deployment stop. `LOCAL_BLOCK != GLOBAL_BLOCK`.

## Families

| Pipeline | Mega roots | Deep-work job |
|---|---|---|
| `control-plane` | always-on-core, adaptive-operations, sovereign-runtime, far-away-party | Session continuity and mission-execution loop |
| `memory-fleet` | omniversal-memory, fleet-harmonizer, docgen-synthesis | Recon, memory synthesis, fleet map |
| `change-swe` | safe-change-orchestrator, self-healing-forge, autonomous-software-engineering, architectural-evolution-engine, dev-fork-orchestrator | Repair, verification, and continued execution |
| `ship-cloud` | web-build-system, vercel-web-foundry, backend-infrastructure-engine, secure-cloud-foundry | Build, package, execute/deploy, readback, and receipt |

## Runner

```bash
python scripts/deep_work_stage.py --list
python skills/pipeline-compositor/scripts/engine.py
python scripts/run_deep_work_pipeline.py --pipeline inception-to-deployment
python tests/test_deep_work_pipelines.py -v
```

Stage commands stay inside `scripts/deep_work_stage.py` so the DAG remains inspectable. Inspectability is an observability property, not a permission stage.
