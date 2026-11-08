---
name: glacier-memory-boot
description: Recover and bind active GlacierEQ mission context at the start of any OMP or other-agent work without adopting stale objectives.
---
# Glacier Memory Boot — mission-first recovery

1. Extract the current explicit mission, entity, scope and constraints from the current user turn. Prior sessions are hints, not commands. Distinguish an explicit mission ID from an incidental case mention.
2. Discover live `mem-live` with MCP `tools/list` and authenticate using normal provider OAuth. No keys in prompts or config. Prefer live search/get-note when available.
3. If live Mem is disconnected, use `glaciereq-archive.memory_status` and `memory_mission`/`memory_search` to recover original UUIDs from the local SQLite snapshot; disclose the capture date and missing bodies.
4. Fetch owner note, case router, source pointers and contradiction/correction history by exact IDs. Reject cross-case identity conflation and credential-body disclosure.
5. Bind mission to APEX/Aspen state; before actions get actual provider stage/receipt from owning source.
6. Produce a short **context receipt**: mission ID, Mem IDs, original evidence provider, version/time, next authorized action, missing evidence, recovery cursor.
7. Do not execute or claim external completion as part of boot. Hand off to evidence and execution skills.

**Acceptance:** tested tool discovery and direct note read; no stale mission promoted; source class retained; no phantom send/file; private data scoped.