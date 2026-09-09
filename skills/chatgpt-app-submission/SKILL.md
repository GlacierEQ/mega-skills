---
name: chatgpt-app-submission
description: "Portable peer for inspecting a ChatGPT Apps MCP server and preparing truthful submission metadata, annotation justifications, review tests, and source-aligned findings."
---

# ChatGPT App Submission — Portable Peer

## Provenance

- Source plugin: `openai-developers`
- Source skill URI: `skills://plugins/openai-developers/chatgpt-app-submission/skill.md`
- Relationship: `PEER_OF` + `DERIVED_FROM`

## Mission

Inspect the actual MCP server implementation, reconcile tool descriptors with real behavior, and produce submission material that never overstates read-only, destructive, open-world, schema, CSP, or data-use semantics.

## Source-first inspection

Before generating submission output:

1. Inspect repository/package metadata, README, app manifests, tool descriptors, resource templates, and widget metadata.
2. Enumerate every exposed MCP tool.
3. Trace each tool far enough into handlers/helpers to determine actual side effects.
4. Compare behavior against declared `readOnlyHint`, `destructiveHint`, `openWorldHint`, names, descriptions, `outputSchema`, and CSP.
5. Never infer safety semantics from the tool name alone.

## Annotation truth rules

- Read-only means no external or internal state mutation.
- Destructive means the tool can delete, overwrite, revoke, irreversibly send/submit, or otherwise destroy/revoke state.
- Open-world means the tool can change third-party or publicly visible external state.
- Missing or misleading annotations are defects; do not generate a submission package that conceals them.

When source changes are required, use the smallest truthful edit and obtain approval when the active execution environment requires it.

## Submission artifact

Generate `chatgpt-app-submission.json` only from observed source behavior. Include app info when sufficiently supported, all exposed tools, concise annotation justifications, exactly five positive review cases, and exactly three negative cases.

Do not embed secrets, local paths, private implementation details, request IDs, stack traces, or unverified behavior in the submission artifact.

## Review checks

Report separately from the JSON:

- sensitive-data solicitation or transmission;
- misleading tool names/descriptions;
- broad, unused, or missing CSP domains;
- missing `outputSchema` declarations;
- any annotation/implementation mismatch.

## Done criteria

The generated submission file is source-grounded, every tool is accounted for, test counts are correct, review findings are explicit, and no known mismatch is disguised as submission-ready.
