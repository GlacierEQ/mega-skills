---
name: openai-platform-api-key
description: "Portable credential-gate peer for OpenAI API-backed builds. Safely determine credential availability, obtain explicit reuse/create intent, provision through an authorized provider surface when available, and never expose plaintext secrets."
---

# OpenAI Platform API Key — Portable Peer

## Provenance

- Source plugin: `openai-developers`
- Source skill URI: `skills://plugins/openai-developers/openai-platform-api-key/skill.md`
- Relationship: `PEER_OF` + `DERIVED_FROM`

## Mission

Act as the credential gate for work that will build, run, test, debug, or configure an OpenAI API-backed artifact. Keep credential decisions separate from application design and prevent plaintext secret exposure.

## Hard safety contract

- Never request, print, quote, summarize, log, or commit a plaintext API key.
- Never inspect secret-bearing files with commands that echo matching values.
- Presence checks must reveal only presence/absence and safe metadata.
- Do not silently reuse an existing key for a new live API workflow.
- Do not create or persist a new key without explicit user authorization and a confirmed destination when a local write is involved.
- Prefer ignored/untracked environment files or an approved secret manager.

## Credential decision gate

Before API-dependent implementation or live testing:

1. Inspect safely for a usable credential without revealing it.
2. If an existing credential is present and the user did not explicitly request a new one, ask whether to reuse it or create a new one.
3. If none is present, ask whether to create/provision one securely.
4. Stop API-dependent implementation until that decision is resolved.

Repository inspection that does not expose secrets may continue only to determine conventions and the safe credential destination.

## Provisioning routing

- When a provider-native OpenAI Platform key-creation surface is available, prefer it.
- Keep organization/project selection and key creation inside the authorized provider flow.
- Transfer secrets only through an approved encrypted/secret-handling path.
- If provider-native provisioning is unavailable, report the missing capability rather than inventing or exposing a key.

## Portable runtime behavior

ChatGPT/Codex may expose provider-specific secure pickers or key-management tools. Other runtimes must preserve the same semantic gates using their own approved secret manager or encrypted transfer path. Host-only mechanics are not assumed portable.

## Done criteria

Credential state is known without secret disclosure, user reuse/create intent is explicit, any persistent destination is confirmed, and live API work proceeds only after a usable credential is safely available.
