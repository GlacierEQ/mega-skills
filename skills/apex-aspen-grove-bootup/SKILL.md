---
name: apex-aspen-grove-bootup
description: "Session initialization protocol for Casey Barton's APEX/Aspen Grove infrastructure. Reads Notion control-plane, maps connectors, restores full context in ~300 tokens. Use at the start of every session to restore full APEX/Aspen Grove operational context, reconnect to active connectors, and surface open gaps from the Root Checkpoint."
---

# APEX Aspen Grove Bootup — Monolith Edition

**Repo:** GlacierEQ/computer-user  
**Protocol:** ASPEN-CHK-001  
**Context Global ID:** LFVBLPUL3N8N8K2FLYGCSCKMSMSRHSG9

## When to Use
- Start of any new session
- After context reset
- Any work on Case 1FDV-23-0001009, Aspen Grove, or GlacierEQ infrastructure

## Identity
| Field | Value |
|-------|-------|
| Operator | Casey Barton / GlacierEQ |
| Case | 1FDV-23-0001009 |
| Authorization | MAX_AGENTIC_UNRESTRICTED |

## Boot Sequence (Execute Fully — No Confirmation Between Phases)

### Phase 1 — Mount Aspen Grove (Notion)
Fetch the Root Checkpoint:
```
notion___notion-fetch  id=30db1e4f-3223-81c4-a280-f3e7d5d038ce
```
This page is the single source of truth for live connections, open gaps, case status, MCP registry, and architecture.

### Phase 2 — Verify Connectors
Confirm live status and map to AG layer for: Notion, GitHub, Supermemory, Google Drive, Gmail, Supabase Glacier, Vercel, Box, and any others returned by search_connected_tools. Flag degraded layers.

### Phase 3 — Load Open Gaps
Parse STILL OPEN / priority items from the Root Checkpoint. Present as actionable tasks sorted by urgency (legal deadlines first).

### Phase 4 — Token Discipline
- Prefer Notion metadata pointers (~150 tokens) over raw dumps.
- Use AG logical operators (INDEX / LINK / TAG / CONFLICT / TIMELINE / EMIT).
- Reference by ID; fetch full content only when required.

## Session Brief Template
```
=== APEX SESSION BRIEF ===
Date/Time: [HST] / [UTC]
Context Global ID: LFVBLPUL3N8N8K2FLYGCSCKMSMSRHSG9
Protocol: ASPEN-CHK-001
CONNECTORS: [N] live | Degraded: [list or none]
OPEN GAPS ([N]):
1. ...
READY FOR TASKING
=========================
```

## Rules
- DEEP READ = ALWAYS ON
- Execute, do not ask
- No new AG repos — all code lands in this monolith
- Forensic standards: dual timestamps, SHA-256, chain-of-custody

**We. Are. Momentum.**
