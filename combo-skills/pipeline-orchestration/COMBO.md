---
id: pipeline-orchestration
display_name: Pipeline Orchestration
schema: ../../schemas/combo-skill.schema.json
version: 1.0.0
status: active
---

# Pipeline Orchestration

## Purpose and selection

Use this Combo Skill when multi-stage data pipelines, cross-cloud sync jobs, or stacked connector sequences must be composed, scheduled, and executed with backpressure, fault recovery, and quality verification. Do **not** use it for trivial single-command scripts.

## Incremental value

This Combo Skill transforms isolated connectors and processing stages into a resilient, dependency-aware Directed Acyclic Graph (DAG) with automated triggers, rate limiting, and state checkpointing verified by formal quality gates.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `pipeline-compositor` | Skill | Yes | Compose stages into a verified DAG with typed edges | Pipeline specification and stage definitions | `pipeline-execution-manifest.json` | DAG is verified acyclic and step inputs resolve |
| 2 | `connector-bridge` | Skill | Yes | Execute cloud connector transfers and API integrations | Step payloads and connection parameters | `connector-response-receipt.json` | Connector transfers succeed with valid status |
| 3 | `quality-gate` | Skill | Yes | Validate stage output invariants, throughput, and error boundaries | Execution manifest and connector receipts | Gate record | Pipeline terminates cleanly within latency and error budgets |

## Ordered execution

1. **DAG composition — `pipeline-compositor`** consumes stage definitions, validates acyclic topological order, produces `pipeline-execution-manifest.json`, and passes when all stage contracts match.
2. **Connector dispatch — `connector-bridge`** consumes stage payloads, executes cloud/database I/O with circuit-breaker protection, produces `connector-response-receipt.json`, and passes when all endpoints return clean status.
3. **Execution gate — `quality-gate`** consumes execution manifests and connector receipts, enforces performance and error boundaries, produces a gate record, and passes when the entire pipeline terminates successfully.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `pipeline-compositor` | `connector-bridge` | Validated DAG execution manifest, stage payloads | Connector response receipts, transfer logs | pipeline architect | DAG topological order is resolved |
| `connector-bridge` | `quality-gate` | Completed transfer receipts, stage checkpoints | Verified quality gate record | quality lead | Connector responses are valid and checkpoints saved |

## Evidence, risks, and state

The Combo must record all stage execution timings, data throughput volumes, error rates, and checkpoint markers in its evidence register. Persist durable checkpoints after each stage.

## Quality gates

The Combo is complete only when all pipeline stages execute to terminal completion, intermediate checkpoints verify data integrity, and `pipeline-orchestration-record.md` is emitted.

## Compound output

**Artifact:** `pipeline-orchestration-record.md`

**Ready for Mega Skill integration when:**

1. Pipeline DAG finishes execution with zero unhandled exceptions.
2. Connector transfers across cloud and database endpoints verify data parity.
3. Quality gate confirms bounded execution latency, checkpoint persistence, and proper resource teardown.
