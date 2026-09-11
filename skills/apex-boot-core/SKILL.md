---
name: apex-boot-core
description: "Bootstrap, health watchdog, and environment normalizer for the APEX Estate. Validates POSIX toolchain permissions, MCP server availability, dev fork overlay status, and system invariants on startup."
---

# APEX Boot Core

## Purpose

Operate as the **master estate initialization and health watchdog sentry**. Executes preflight environment verification, checks permission parity across command binaries in `~/.local/bin/`, verifies MCP gateways, and guarantees zero runtime drift.

## Startup Invariants Checked

1. **POSIX Toolchain Perms**: Validates that all estate binaries have executable permissions (`0o755`).
2. **MCP Gateway Readiness**: Probes OpenRouter, GitHub, Notion, Supabase, and local memory bridges.
3. **Dev Fork Overlay Integrity**: Verifies pristine upstream bases and detached overlay extensions.
4. **Epistemic Environment Status**: Calibrates local tooling and reports baseline Epistemic Tier.

## Standard Procedure and Workflow

1. **Preflight**: Execute `python scripts/boot_watchdog.py --check` to scan toolchain status and binary modes.
2. **Gateway Probe**: Validate active MCP server socket connectivity and authentication headers.
3. **State Normalization**: Correct file permissions (`chmod 0755`) for local executable scripts when drifts occur.
4. **Receipt Generation**: Emit machine-readable readiness state receipt for downstream agent orchestration.

