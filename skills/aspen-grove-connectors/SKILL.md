---
name: aspen-grove-connectors
description: "Evidence-safe multi-service connector mesh for GlacierEQ. Models provider health, dispatch, and multi-plugin coalitions without promoting configuration, credentials, mocks, or unbound transports into verified provider state."
---

# Aspen Grove Connectors Mesh

Aspen Grove is the connector envelope for composing external services into reusable pipelines.

## Evidence law

- **Credential present != provider verified.**
- **Runtime tool exposure != authenticated connection.**
- **Mock/sandbox output is SIMULATED, never VERIFIED.**
- **A bound provider call without an explicit verification receipt remains SOURCE_BOUND.**
- **Only an explicit provider-native receipt may promote a connector/action to VERIFIED.**
- **Unbound live transports block. They never return fabricated live success.**

## Current connector surface

The default mesh includes GitHub, Notion, Supabase, Dropbox, Linear, ClickUp, Vercel, DuckDB, Pinecone, Taskade, Gmail, Google Drive, Slack, MemoryPlugin, Mem0, and E2B. Additional services may be injected dynamically.

A service being listed here means the mesh can model it. It does **not** mean credentials, OAuth, provider health, or write authorization are current.

## Pipeline composition

`AspenGroveMesh.plan_pipeline(stages)` evaluates a connector coalition before execution. Required stages are runnable only when their provider health receipt explicitly sets `verified=true`.

Use `integrations/chatgpt-plugin-runtime-snapshot.json` for the current ChatGPT runtime exposure census and `integrations/chatgpt-plugin-coalitions.json` for reusable multi-plugin DAG contracts.

## Verification

Focused behavior tests live at:

`skills/aspen-grove-connectors/tests/test_evidence_semantics.py`

They guard against the prior failure mode where credential presence was labeled "online (live)" and an unbound live request returned a fabricated success payload.
