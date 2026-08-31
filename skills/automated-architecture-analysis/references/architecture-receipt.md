# Architecture Dependency Analysis Receipt

Use this template after analyzing or changing an architecture dependency graph. Attach the raw graph and machine-readable results when possible.

| Field | Value |
|---|---|
| Authorization and owner | `<approver, scope, and policy owner>` |
| Repository and commit | `<repo>@<commit>` |
| Architecture question | `<cycle, layering, coupling, migration, or drift question>` |
| Sources and tools | `<manifests, imports, build graph, extractor versions, ruleset>` |
| Scope and exclusions | `<roots, languages, generated/vendor/test paths, external systems>` |
| Graph model | `<node/edge types and direction semantics>` |
| Graph size | `<nodes, edges, unresolved edges, extraction confidence>` |
| Findings | `<cycles/SCCs, forbidden edges, coupling, depth, reachability>` |
| Ranked risks | `<blast radius, ownership, build/runtime/security impact, confidence>` |
| Mitigation | `<inversion, port, extraction, event boundary, ownership transfer, adapter>` |
| Changed files | `<paths and graph delta>` |
| Verification | `<architecture checks, focused/full tests, build, generated validation>` |
| Tower route | `<not applicable, or preflight → source-of-truth → exhibits/proof → validate → generate → test → build → integrity → receipt>` |
| Policy gate | `<command, threshold, fail-closed conditions>` |
| Exceptions | `<owner, rationale, compensating control, expiry; write “none” when absent>` |
| Residual risk | `<unresolved edges, allowed cycles, workload or tool limitations>` |
| Rollback | `<revert commit, adapter removal, or restoration command>` |
| Release decision | `<pass, block, or escalate with reason>` |
| Next action | `<merge, migrate, monitor, retry, or retire>` |
