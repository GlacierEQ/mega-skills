---
name: openai-agents-sdk
description: "Portable GlacierEQ peer for the ChatGPT openai-developers Agents SDK skill. Build, test, evaluate, and deploy OpenAI Agents SDK applications while preserving live documentation, credential, safety, and verification gates."
---

# OpenAI Agents SDK — Portable Peer

## Identity and provenance

- Source plugin: `openai-developers`
- Source skill URI: `skills://plugins/openai-developers/agents-sdk/skill.md`
- Source skill name: `agents-sdk`
- Portable peer name: `openai-agents-sdk`
- Edge semantics: `PEER_OF` + `DERIVED_FROM`
- Collision note: `skills/agents-sdk` already represents Cloudflare's Agents SDK and must remain distinct.

The ChatGPT-hosted source remains authoritative for its own runtime semantics. This package carries the reusable execution contract into Mega-Skills without claiming host-only behavior was copied.

## Mission

Turn an idea, repository, or prior agent design into a runnable OpenAI Agents SDK application with explicit tools, state, approval gates, verification, and an observable proof path. Prefer Python unless the active mission or repository clearly requires TypeScript.

## Preconditions

1. Hydrate the target repository and nearest valid continuation before editing.
2. Retrieve current OpenAI Agents SDK documentation before relying on API syntax or deployment behavior.
3. If a live OpenAI API request will occur, route credential handling through `openai-platform-api-key`; never expose plaintext secrets.
4. Preserve the repository's package manager, naming, architecture, and verified gains unless a change is materially justified.

## Build contract

1. Define the agent goal, input/output contracts, tools, state, approvals, and proof command.
2. Start with one agent; add specialists or handoffs only when the workflow actually requires them.
3. Model deterministic actions as explicit tools with narrow schemas and bounded side effects.
4. Use sandbox/workspace execution only for workflows that genuinely require file, shell, or isolated workspace access.
5. Keep runtime instructions, application code, evals, sample data, and deployment artifacts distinguishable.
6. Provide a local smoke path. For HTTP services, expose a readiness/health endpoint when practical.

## Evaluation contract

When evals are requested or materially useful:

- exercise the real agent path rather than a mock-only path;
- cover happy path, missing evidence, forbidden/required tool use, approval gates, state transitions, and known regressions;
- grade behavior, tool calls, traces, and state rather than volatile IDs or cosmetic prose;
- persist machine-readable results and fail the runner when contract checks fail.

## Deployment contract

When deployment is requested:

- use the strongest available runtime-native deployment mechanism;
- verify manager/runtime health and the application's own readiness path;
- preserve generated deployment artifacts and report them;
- make deployment claims only with provider/runtime readback.

## Portable runtime routing

- ChatGPT/Codex with OpenAI developer capabilities: prefer provider-native documentation, credential, and deployment surfaces.
- Local Codex/CLI: use repository tools, local runtime, and explicit secret handling.
- Other GlacierEQ runtimes: preserve this contract and map actions to equivalent repository, shell, deployment, and secret-management capabilities.

Never claim a host-only capability is portable until the peer has independent execution evidence.

## Done criteria

The application has an executable entrypoint, a documented proof command, observable output, and explicit verification or blocker evidence. Deployment requires provider/runtime readback.
