# Inception-to-Deployment Deep-Work Pipelines

Mega Skills already describe complete workflows. These pipelines make that
description **executable** without turning the repository into an autonomous
deployer.

## Span

```text
inception → readiness → recon → design → build
        → verify → package → deploy-gate → handoff → evolve
```

Every family pipeline covers the same span. The master pipeline
`inception-to-deployment` is the only graph that is allowed to claim the
full product loop.

## Deploy rule

`deploy_mode` is `approval_packet_only`.

Pipelines may:

- validate hierarchy and Combo/Mega contracts
- run local tests
- write run artifacts and receipts
- emit a deployment decision packet

Pipelines may not:

- mutate remotes
- send network
- merge
- deploy
- access credentials
- file legal instruments

A `READY_PENDING_HUMAN_APPROVAL` packet is the terminal deploy-gate result.
Observed production change requires a separate human-approved mission.

## Families

| Pipeline | Mega roots | Deep-work job |
|---|---|---|
| `control-plane` | always-on-core, adaptive-operations, sovereign-runtime, far-away-party | Session continuity and guarded operating loop |
| `memory-fleet` | omniversal-memory, fleet-harmonizer, docgen-synthesis | Recon, memory synthesis, fleet map |
| `change-swe` | safe-change-orchestrator, self-healing-forge, autonomous-software-engineering, architectural-evolution-engine, dev-fork-orchestrator | Bounded repair and verification |
| `ship-cloud` | web-build-system, vercel-web-foundry, backend-infrastructure-engine, secure-cloud-foundry | Build, package, approval-gated ship packet |

## Runner

```bash
python scripts/deep_work_stage.py --list
python skills/pipeline-compositor/scripts/engine.py   # compositor API
python scripts/run_deep_work_pipeline.py --pipeline inception-to-deployment
python tests/test_deep_work_pipelines.py -v
```

Stage commands stay inside `scripts/deep_work_stage.py` so the DAG cannot
grow hidden shell one-liners.
