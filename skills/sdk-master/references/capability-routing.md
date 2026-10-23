# SDK Master — capability routing and source literacy

## 1. Determine what you're actually interacting with

| Layer | Evidence | What it proves | What it does not |
| --- | --- | --- | --- |
| Lockfile/package manifest | resolved package + version or constraint | dependency intent / resolved dependency | import success, runtime compatibility |
| Installed package / source and declarations | package version, exported names, actual type signatures | local callable surface to test | provider acceptance |
| Official exact-version docs | version-tagged reference, migrations, release history | documented intended semantics | deployed/installed surface parity |
| API contract | official OpenAPI/AsyncAPI/Proto/JSON Schema | wire-level shape, where complete | SDK implementation quality |
| Unit and type tests | executed build/test outputs on current head | tested local behavior | live integration success |
| Provider request/response | structured result, status, request ID | attempted or acknowledged operation | final intended external state |
| Provider readback | stable provider IDs and independent state retrieval | observed state at readback time | lasting correctness absent ongoing probes |

Separate **observed**, **inferred**, **disputed** and **unknown** facts. Pin dates/revisions on volatile upstream documentation. Prefer source and actual declarations over blog examples for call signatures, but use the canonical wire contract and live provider behavior for externally visible semantics.

## 2. Choose the correct strategy

- **Existing official SDK**: prefer when maintained, version-compatible, typed enough, and supports required actions. Do not replace it with raw HTTP without a documented deficiency.
- **Existing internal SDK/adapter**: reuse and repair when it already supplies idempotency, tenancy, provenance or domain contracts. Trace delegation: a payload builder is not an executor.
- **Generated SDK**: prefer when a high-quality authoritative OpenAPI/Proto exists and multiple language consumers need consistency. Pin generator and review diffs for semantic gaps.
- **Handwritten SDK extension**: justify for SDK omissions, streaming, nonstandard authentication or provider quirks. Expose a disciplined public surface and tests, not per-endpoint patches.
- **Direct API integration**: use if SDK is unavailable/outdated or incompatible, with official contract, safe transport and a migration path. Do not invent undocumented HTTP fields.

Language fit: TypeScript/JavaScript package exports + `.d.ts` + lockfile; Python wheel metadata, importable source, `py.typed`, type checking; Go module package public identifiers + `go.mod`/`go doc`; Rust crates/docs, public traits and features; Java Maven/Gradle API signatures; .NET NuGet package/version and generated XML or public assembly surface. Preserve language/runtime conventions. Do not introduce a new language to advertise breadth.

## 3. Non-negotiable API literacy

Audit all applicable categories: authentication/scopes/tenant isolation; HTTP error mapping and SDK exceptions; timeouts, cancellation and context propagation; pagination and filtering semantics; rate limits and `Retry-After`; retries limited to safe/idempotent actions; idempotency keys and ambiguous-write reconciliation; streaming/SSE/WebSockets backpressure and abort; request/response schema evolution, null vs absent and unknown enum members; large identifiers and precision; concurrency and connection reuse; observability, trace/request IDs; secrets and PII redaction; package ABI/runtime compatibility; semver and upgrade/migration path; license/supply chain and reproducible install.

## 4. Selection receipt

Record the SDK package/provider, version constraints **and verified installed version**, target language/runtime, selected specialist skills with path/revision, official documents with their version/date, source code locations, relevant contract revision, behavioral proof commands and provider-readback status. Do not treat any single source or any one green status as a substitute for the rest.
