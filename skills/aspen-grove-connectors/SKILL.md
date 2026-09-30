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

## Worker execution rules

Apply the executable policy in `worker_policy.py` on every plugin-expansion run:

1. Fresh provider-native evidence outranks stale aggregate projections; stale snapshots may not demote stronger later evidence.
2. Do not retest a VERIFIED core surface without a concrete regression signal or explicit recheck.
3. Do not retry the same transiently blocked route unless provider state changed or the route is materially different.
4. Blockers change route, not objective; preserve the unresolved slice explicitly.
5. A write is not VERIFIED_WRITE until provider acceptance, independent owning-provider readback, and explicit exercised scope all exist.
6. Verification is surface-scoped; never generalize one exercised action into unrelated provider capability.
7. Never guess among multiple provider accounts/workspaces in non-interactive execution.
8. Before security mutations, recover current state, legitimate access paths, intended roles, and a post-mutation readback plan.
9. A failed deployment on a stale commit is not evidence current source is broken; compare source first.
10. Every run must create a material delta: newly verified capability, repaired seam, or strengthened reusable coalition.

Machine-readable contract: `integrations/plugin-worker-beneficial-rules.json`.
Focused behavior tests: `tests/test_worker_policy.py`.
