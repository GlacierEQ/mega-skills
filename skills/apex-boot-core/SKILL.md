---
name: apex-boot-core
description: "Bootstrap, health watchdog, and environment normalizer for the APEX Estate. Validates POSIX toolchain permissions, MCP server availability, dev fork overlay status, and system invariants on startup."
---

# APEX Boot Core

Operate as the **master estate initialization and health watchdog sentry**. Executes preflight environment verification, checks permission parity across command binaries in `~/.local/bin/`, verifies MCP gateways, and guarantees zero runtime drift.

## Startup Invariants Checked

1. **POSIX Toolchain Perms**: Validates that all estate binaries have executable permissions (`0o755`).
2. **MCP Gateway Readiness**: Probes OpenRouter, GitHub, Notion, Supabase, and local memory bridges.
3. **Dev Fork Overlay Integrity**: Verifies pristine upstream bases and detached overlay extensions.
4. **Epistemic Environment Status**: Calibrates local tooling and reports baseline Epistemic Tier.
