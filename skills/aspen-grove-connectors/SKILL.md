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

## Hidden-harm counter-engineering

A connector transition can be harmful without being factually false. Before accepting a route, projection, fallback, demotion, or mutation, evaluate what capability or meaning would be lost.

Protect these dimensions:

- **Authority domain:** Operator-reported facts, provider-native facts, memory projections, and inference remain distinct. Failure to recover a provider artifact never erases a legitimate fact from another authority domain.
- **Negative evidence:** Retrieval failure is not falsity, and zero matches from partial coverage is not proof of absence.
- **Fallback parity:** A fallback is equivalent only when it preserves the required capability set. Otherwise label it `DEGRADED_FALLBACK` and name the lost capabilities.
- **Projection fidelity:** Preserve authority, provenance, evidence state, and contradictions across projections. Block a projection that silently drops protected semantics.
- **Demotion safety:** Stronger evidence may be demoted only by disconfirming provider-native evidence for the same scope. A scope change requires a split state, not a global downgrade.
- **Reversible mutation safety:** For reversible connector writes, capture pre-state, retain a rollback route, and use idempotency before mutation.
- **Continuation preservation:** Route changes must keep the objective, unresolved slice, and strongest known cursor intact.
- **Privacy boundary:** Private or restricted source material may not silently widen into a less restrictive projection; preserve the boundary or require explicit declassification/redaction.

Counter-pattern:

`DETECT LOSS -> NAME LOST DIMENSION -> PRESERVE STRONGER STATE -> ROUTE AROUND -> VERIFY -> PERSIST`

Executable gates live in `worker_policy.py`; regressions are locked by `tests/test_hidden_harm_policy.py`.

## Hidden-harm connector owner

Compose `hidden-harm-connectors` for every material provider/plugin/MCP transition. Aspen Grove owns connector mechanics and evidence semantics; the specialist owns cross-transition loss analysis, including fallback parity, account ambiguity, projection loss, privacy widening, scope overgeneralization, reversible-write prestate, and unjustified demotion.

A route is not considered equivalent merely because it executes successfully.

