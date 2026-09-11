---
name: apex-aspen-grove-bootup
description: "Aspen Grove boot/continuation protocol for GlacierEQ missions with secret-safe context routing."
---

# APEX Aspen Grove Bootup

## Purpose
Rehydrate the nearest valid continuation state for an Operator mission without embedding credentials, private tokens, or provider-specific secret values in source control.

## Identity and routing
- Operator/project/case identity must be recovered from current Operator direction plus qualified continuity sources.
- Provider-specific context IDs or credentials must be supplied at runtime through secret-safe configuration or source-bearing records; never hard-code their values in this skill.
- Session protocol identifiers may be public/non-secret configuration, but must not be confused with authentication material.

## Boot sequence
1. Read current Operator command and preserve its operation class.
2. Reuse relevant known state before rediscovery.
3. Recover nearest durable continuation point and active obligations.
4. Hydrate only material unknown, changed, conflicting, or source-native state.
5. Preserve provenance, contradictions, versions, receipts, and unresolved dependencies.
6. Route to the qualified skills/tools needed for the mission.
7. Execute rather than substituting boot/status work for the mission.
8. Verify provider-side mutations with readback where supported.
9. Persist a lossless continuation record without secrets.

## Memory mesh
Treat Mem0, MemoryPlugin, Supermemory, vector stores, Notion, Supabase, files, repositories, provider receipts, and other qualified sources as provenance-bound peers. No peer becomes globally canonical by appearing in this boot skill.

## Secret boundary
Never commit API keys, tokens, private context identifiers that function as credentials, passwords, cookies, session secrets, or raw authentication material. Configuration may reference environment-variable names or secret-manager identifiers only.

## Session brief template

```text
=== APEX SESSION BRIEF ===
Date/Time: [local] / [UTC]
Context locator: [runtime-resolved, redacted if sensitive]
Protocol: ASPEN-CHK-001

MISSION: [current Operator mission]
NEAREST VALID CONTINUATION: [source-bearing pointer]
KNOWN STATE REUSED: [material prior gains]
MATERIAL STATE HYDRATED: [sources/providers]
CONTRADICTIONS: [preserved, unresolved/resolved]
EXECUTION: [actions actually performed]
VERIFICATION: [provider/tool receipts]
NEXT FRONTIER: [exact executable continuation]
=== END BRIEF ===
```

## Completion law
Bootup is support work. It is successful only when it enables the requested mission to advance; a session brief by itself is not substantive progress unless the Operator specifically requested that artifact.
