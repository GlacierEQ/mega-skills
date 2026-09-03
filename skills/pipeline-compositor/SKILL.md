---
name: pipeline-compositor
description: "Durable DAG pipeline runtime for composing skills, scripts, connectors, and agents with dependency validation, bounded parallelism, retries/timeouts, artifact hashing, checkpoint/resume, and execution manifests."
---

# Pipeline Compositor

## Purpose

Turn multi-stage work into a durable, resumable execution graph instead of an ephemeral sequence of prompts or shell commands.

The compositor is company-agnostic. Domain-specific pipelines live under `pipelines/` and bind mission data to the generic runtime.

## Core invariants

1. Every stage has a stable ID and explicit command.
2. Dependencies must resolve and the graph must remain acyclic.
3. Stage commands are executed without a shell.
4. Workspace paths must stay inside the declared workspace.
5. Produced artifacts must exist before a stage is recorded as successful.
6. Resume-safe stages are skipped only when the pipeline spec and prior input/output artifact hashes still match.
7. Checkpoints are written atomically.
8. Failures stop downstream execution and remain visible in the manifest.
9. Parallelism is bounded by both the pipeline contract and the runtime override.
10. Execution claims come from receipts/manifests, not from documentation alone.

## Runtime

Primary engine: `skills/pipeline-compositor/scripts/engine.py`

Primary CLI:

`python skills/pipeline-compositor/scripts/run.py --pipeline <pipeline.json> --workspace . --state-dir <dir> --resume`

Diagnostic entrypoints:
- `dag_parser.py`
- `topology_validator.py`
- `stage_executor.py`
- `checkpoint_manager.py`
- `backpressure_controller.py`
- `manifest_synthesizer.py`

## Durable outputs

Executions produce stage receipts, atomic checkpoint state, deterministic DAG layers, artifact hashes, terminal status, and a declared pipeline execution manifest.

## Resume semantics

Resume is hash-validated, not merely ID-based. A stage resumes only when it is explicitly `resume_safe`, the pipeline spec matches, the prior state succeeded, and current consumed and produced artifact hashes still match the recorded receipt.

## Verification

Behavioral tests must prove cycle rejection, deterministic dependency layering, real subprocess execution, checkpoint persistence, and hash-validated resume behavior.

## First production composition

`pipelines/anthropic-applied-ai-readiness.json`

This demonstrates:

`generic durable runtime → versioned target-role contract → evidence projection → verification → durable mission artifacts`

Anthropic-specific requirements remain data-driven and outside the scheduler.

## Boundaries

- Do not invent missing artifacts.
- Do not mark failed stages successful.
- Do not silently continue past a failed dependency.
- Do not use resume to hide changed inputs or outputs.
- Do not embed secrets in pipeline definitions or manifests.
- Do not conflate local validation with CI success.
