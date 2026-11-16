---
name: hidden-harm-connectors
description: "Counter-engineer hidden harms in connectors/plugins/MCP: prevent false verification, weaker-fallback substitution, account ambiguity, projection loss, unsafe writes, privacy widening, scope overgeneralization, and provider-state demotion."
---

# Hidden Harm — Connectors Calibrator

> Chassis wheel. Governance polarity → `hidden-harm-governance` / `gate_polarity`. This skill owns connector/MCP loss detection; it does not invent permission ladders.

## Mission

Ensure connectors increase capability without silently weakening evidence, authority, privacy, reversibility, or the human objective. Runtime exposure is not provider truth; a working fallback is not automatically equivalent; a successful request is not verified state until read back.

## Protected dimensions

- provider-native provenance
- verification scope
- capability surface
- write/readback ability
- account/workspace binding
- privacy boundary
- reversible pre-state/rollback
- evidence strength
- continuation cursor
- Operator objective served

## Hidden harms to detect

1. runtime/tool exposure promoted to provider verification;
2. credentials/configuration promoted to health;
3. a weaker fallback presented as equivalent;
4. provider account/workspace guessed under ambiguity;
5. write success promoted without independent owning-provider readback;
6. one verified action generalized to unrelated actions;
7. a stale aggregate snapshot demoting fresher provider evidence;
8. projection dropping authority/provenance/contradictions;
9. private/restricted data widening through a target connector;
10. repeated blocked-route retries consuming the run while stronger routes exist;
11. security mutation breaking legitimate access because pre-state/roles were not recovered.

## Execution

Use the Aspen Grove evidence and worker-policy contract:

`DISCOVER -> READ -> CAPABILITY/PERMISSION DIFF -> HIDDEN-HARM GATES -> USEFUL WRITE WHEN JUSTIFIED -> PROVIDER READBACK -> SCOPED VERIFIED STATE -> COALITION INTEGRATION -> DURABLE CURSOR`

Required checks:

- fallback parity
- authority-aware reconciliation
- negative-result interpretation
- projection-loss gate
- privacy-boundary gate
- reversible-write prestate
- demotion gate
- account disambiguation
- stale deployment/source comparison

## Success

A connector is successful only for the surface actually exercised, and only when it materially enables a useful workflow without silently dropping stronger capability or meaning. Prefer route changes over objective reduction.
