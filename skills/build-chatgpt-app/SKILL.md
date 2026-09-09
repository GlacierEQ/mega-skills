---
name: build-chatgpt-app
description: "Portable peer for designing, scaffolding, refactoring, and validating ChatGPT Apps SDK applications built from an MCP server plus optional widget UI."
---

# Build ChatGPT App — Portable Peer

## Provenance

- Source plugin: `openai-developers`
- Source skill URI: `skills://plugins/openai-developers/build-chatgpt-app/skill.md`
- Relationship: `PEER_OF` + `DERIVED_FROM`
- Runtime state: portable implementation contract; provider-specific APIs must be revalidated against current OpenAI documentation.

## Mission

Build the smallest coherent ChatGPT Apps SDK implementation that satisfies the requested workflow while preserving accurate tool schemas, side-effect annotations, MCP Apps bridge behavior, widget security metadata, and an observable test path.

## Docs-first gate

Before creating or materially changing an Apps SDK implementation, retrieve current OpenAI Apps SDK documentation for the relevant MCP server, UI/widget, tools, reference, examples, deployment, and submission surfaces. Current provider documentation outranks stale examples or model memory.

## Archetype selection

Choose one primary shape before coding:

- `tool-only`
- `vanilla-widget`
- `react-widget`
- `interactive-decoupled`
- `submission-ready`

Use the smallest archetype that still satisfies the mission. Do not escalate to submission-ready merely because the app might be published later.

## Tool contract

Plan tools before code:

1. One clear job per tool.
2. Explicit machine-friendly inputs.
3. Accurate read/write/destructive/open-world/idempotency semantics.
4. Reusable structured outputs separated from widget-only metadata.
5. For connector-like or knowledge/search apps, prefer standard search/fetch behavior where current Apps SDK guidance supports it.

## Implementation contract

1. Prefer a close official OpenAI example when one matches the requested interaction pattern.
2. Otherwise prefer a version-matched MCP Apps example before inventing a large custom scaffold.
3. Register MCP tools and UI resources explicitly.
4. Use the MCP Apps bridge as the portable baseline; add ChatGPT-specific host APIs only when they materially improve the experience.
5. Keep widget CSP/domain metadata narrow and behavior-aligned.
6. Version resource identifiers when UI changes require cache separation.
7. Keep mutation handlers retry-safe or document non-idempotency explicitly.

## Validation ladder

Run the strongest feasible checks in order:

- static repo/tool-contract review;
- syntax/type/compile checks;
- MCP endpoint/tool-list verification;
- widget/resource verification;
- MCP Inspector or equivalent protocol test;
- ChatGPT Developer Mode integration test when available;
- hosted endpoint verification for production work.

Report exactly which levels were verified and which remain unverified.

## Portability boundary

Do not emulate host-only `window.openai` or ChatGPT UI behavior in another runtime and call it verified. Preserve equivalent semantic contracts where possible, and label host-specific behavior as provider-bound until observed in that provider.

## Done criteria

The repository satisfies its chosen archetype, exposes the intended MCP tools, has accurate annotations/security metadata, includes a reachable local proof path, and has evidence for the validation level claimed.
