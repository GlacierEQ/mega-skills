---
name: connectivity-hub
description: "Universal multi-protocol connectivity hub. Orchestrates WebSockets, Cap'n Proto zero-copy streams, HTTP/2 RPCs, and gRPC endpoints across agent swarms."
---

# Universal Connectivity Hub

The Connectivity Hub manages multi-protocol transport channels across distributed local runtimes (Antigravity, Kilo Code, OpenCode Zen) and remote compute horizons.

## Protocols Supported
- **POSIX Shared Memory / Ring Buffer**: Sub-millisecond zero-copy IPC via memory-mapped ring buffers.
- **Cap'n Proto RPC**: Binary serialized RPC channels.
- **HTTP/JSON-RPC**: Standard REST and JSON-RPC gateways for browser interfaces.
- **WebSocket Streaming**: Real-time bidirectional telemetry for Mission Control.

## Contract Completion

The original instructions above are preserved verbatim; the sections below complete the skill contract.

## Use When

Use this skill when the requested task matches the capability described above and this is the most specific available skill for the work.

## Operating Method

1. Recover the exact Operator objective, existing mission graph, corrections, verified gains, source pointers, and completion test.
2. Refresh relevant owning-source state and reconcile it with recovered evidence before treating a historical gap or task label as current.
3. Map affected workstreams, critical dependencies, useful independent routes, and downstream consequences; load the resources needed to cover that work.
4. Select and execute the strongest coherent workflow by outcome gain, dependency unlock, evidence value, and preservation of verified strengths. Skill ownership scopes each operation; it never shrinks the mission.
5. Verify the resulting state, propagate material corrections across affected work, and continue through reachable authorized work. A prepared next action or completed artifact is a checkpoint; completion requires the requested outcome.
6. Report the resulting outcome and observable proof, unfinished obligations, and exact continuation frontier. Never claim execution that did not occur.

## Progressive Disclosure

Keep the core procedure concise. Load detailed references, scripts, and tests only when they are needed.

### Scripts
- scripts/run.py
- scripts/this_skill.py
- skill.py

### Tests
- tests/__pycache__/test_connectivity_hub.cpython-311.pyc
- tests/test_connectivity_hub.py

## Verification

Instruction readiness and executable readiness are separate. Scripts and integrations must earn behavioral proof through the repository readiness assay before they are described as executed or behavior-verified.

## Boundaries

- Do not invent missing implementation.
- A package-discovery adapter is not evidence of domain execution.
- Preserve upstream provenance and existing project semantics.
- Report unavailable credentials, services, or destructive dependencies precisely instead of fabricating success.
