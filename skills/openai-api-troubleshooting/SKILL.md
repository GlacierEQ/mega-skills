---
name: openai-api-troubleshooting
description: "Portable peer for classifying concrete OpenAI API failures and routing the smallest evidence-backed remediation across transport, authentication, quota, rate-limit, and access failures."
---

# OpenAI API Troubleshooting — Portable Peer

## Provenance

- Source plugin: `openai-developers`
- Source skill URI: `skills://plugins/openai-developers/openai-api-troubleshooting/skill.md`
- Relationship: `PEER_OF` + `DERIVED_FROM`

## Mission

Classify an OpenAI API failure from concrete runtime evidence, name the failure class, and route the next action without conflating network, credential, billing/quota, rate-limit, or project/model-access failures.

## Evidence order

1. Determine whether the request reached the OpenAI API at all.
2. Prefer concrete HTTP status, API error code, response message, retry metadata, and request context over generic heuristics.
3. Retrieve current OpenAI documentation when remediation depends on behavior that can change.
4. Do not rotate/create credentials inside this skill; route credential work to `openai-platform-api-key`.

## Failure classes

### Transport / environment

DNS, connection timeout/reset, blocked outbound access, or other failure before an OpenAI response. Repair or change the execution path before diagnosing API authentication/quota semantics.

### Authentication

Concrete 401/invalid-key/missing-key evidence. Treat as authentication failure and route credential provisioning/configuration through the credential peer.

### Quota / credit exhaustion

Concrete `insufficient_quota`, exhausted balance, or spend-cap evidence. Keep distinct from transient throttling even when both use HTTP 429.

### Rate limiting

Requests/tokens-per-window or retry-after throttling without quota exhaustion. Prefer pacing, batching, exponential backoff, and bounded concurrency.

### Model / project / organization access

Concrete 403, model-not-found, project/org mismatch, or permission evidence. Inspect model/project/org/key scope before guessing.

## Output contract

Keep the user-facing diagnosis compact:

- observed failure class;
- strongest supporting evidence;
- next executable action;
- only the uncertainty that materially affects the next step.

## Done criteria

The failure is assigned to a supported truth state from concrete evidence, the next action addresses that class, and no unrelated remediation is recommended merely because it is common.
