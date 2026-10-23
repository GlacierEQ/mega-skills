# SDK Master — executable conformance and evidence gates

## Test matrix

| Surface | Required meaningful proof |
| --- | --- |
| Public API | import/typecheck and version-supported exports; no guessed identifiers |
| Serialization | encoded request has contract-correct method, path, headers, body, and optional/null semantics |
| Success | real decoder handles exact fixtures and stable identifiers without numeric corruption |
| Errors | auth failure, validation, 404, 409, 429, 5xx, network timeout, cancellation and safe diagnostics |
| Pagination | boundary conditions, cursor exhaustion, duplicate prevention, ordering when guaranteed |
| Auth | correct scope/tenant, no tokens in logs, user-agent/traces sanitized |
| Retry | bounded exponential backoff/jitter, `Retry-After` if documented; no blind write retries |
| Idempotency | stable key where supported, conflicting state handling and freeze/readback on ambiguity |
| Streams | chunk accumulation, abort, re-connect rules, backpressure and partial results |
| SDK version | old/new migration compatibility, pinned lockfile, package/build exports |
| Cross-runtime | representative real build and package consumption at supported runtimes |
| External state | authorized sandbox/live call, provider IDs, independent readback against desired state |

Use **red → green → refactor** for behavior changes. Challenge with counterexamples and tests at the adapter/provider seam. Synthetic fixtures are labeled synthetic; do not infer provider parity from them. Select the strongest applicable tests, not test-count padding. Do not downgrade material test failures to warnings.

## Provider acknowledgement / uncertainty protocol

Use explicit states: `NOT_ATTEMPTED → ATTEMPTED → ACKNOWLEDGED → PROVIDER_CONFIRMED → RECONCILED`. On ambiguous timeout or lost acknowledgement after a write, move to `RECONCILING`; freeze retry; query by stable external ID or an idempotency key; distinguish **applied**, **absent** and **unknown**. Only retry when absence is established and retry semantics are safe. Provider-created objects and local SDK-generated request objects are not interchangeable evidence.

## SDK evidence receipt (example structure)

```json
{
  "sdk": {"provider": "example", "package": "example-sdk", "declared_version": "^2.1.0", "installed_version": null},
  "repository": {"path": "repo", "head_sha": "<verified-commit>"},
  "sources": [{"kind": "package_source", "path": "node_modules/example-sdk/dist/index.d.ts", "revision": null}],
  "contract": {"kind": "openapi", "revision": null},
  "tests": [{"command": "<actual command>", "exit_code": null, "result": "NOT_RUN"}],
  "provider": {"operation": null, "external_id": null, "readback": "NOT_RUN"},
  "verified_level": "DISCOVERED",
  "open_gaps": ["Provider connection not exercised"],
  "next_cursor": "Run exact-version SDK integration fixture and authorized provider readback"
}
```

Do not populate sample values as if they were actual test or provider receipts. Preserve actual commands, output snippets, request IDs where safe, checked code SHA, and the definition of desired state. A green local static check certifies neither the agent's behavior nor SDK integration in production.
