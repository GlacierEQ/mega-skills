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
