---
name: pipeline-compositor
description: Directed Acyclic Graph (DAG) pipeline composition engine for stacking connectors, skills, and agents with typed edges, backpressure, checkpoint/resume, and parallel execution.
---

# Pipeline Compositor

## Purpose

Compose isolated skills, connectors, and agent runtimes into structured, fault-tolerant execution DAGs. Enforce strict type contracts between stages, dynamic fan-out, backpressure control, and durable state checkpointing.

## Procedure

1. Parse the pipeline definition, verifying all step dependencies and input/output edge types.
2. Validate graph topology to ensure acyclic properties (topological sort verification).
3. Initialize pipeline state checkpoints and recovery journals.
4. Execute stages sequentially or in parallel batches according to dependency resolution.
5. Apply backpressure control and rate-limit throttles between high-throughput producers and consumers.
6. Checkpoint intermediate artifacts after each stage completion.
7. Synthesize final multi-stage execution manifest with full traceability.

## Output contract

Produce `pipeline-execution-manifest.json` with step timings, data volumes, intermediate checkpoint references, and stage exit codes.

## Local validation

The procedure passes only when the pipeline DAG executes from source to terminal nodes without type mismatch errors, all intermediate assertions succeed, and execution manifests are fully populated.

## Non-goals

Do not execute unbounded recursive pipelines. Do not silently swallow step failures without triggering defined recovery or rollback policies.
