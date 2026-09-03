# HANDOFF — Anthropic Applied AI

## Verified durable state

- `skills/pipeline-compositor/scripts/engine.py` exists on `main`.
- The former compositor execution stubs have been replaced with executable wrappers.
- `skills/pipeline-compositor/tests/test_pipeline_compositor.py` contains behavioral tests.
- `pipelines/anthropic-applied-ai-readiness.json` exists.
- `target-role.json` and `target-competency-map.json` exist.
- The isolated validation harness completed the two-stage Anthropic pipeline successfully.
- Bootstrap transport files were removed from the repository.

## Exact next action

Build the **evidence inventory stage**.

It must retrieve/inspect actual candidate artifacts and emit structured evidence records with:

- claim
- source
- artifact
- verification method
- epistemic state
- Anthropic competency domain
- hiring-signal strength
- gap or contradiction
- next strengthening action

Then add that stage to `pipelines/anthropic-applied-ai-readiness.json` after `verify-target`.

## Do not restart

Continue from the existing target contract and compositor runtime. Do not recreate the role taxonomy or replace the pipeline with a prose-only workflow.
