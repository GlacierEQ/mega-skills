---
name: telecommunications-execution-core
description: "Validate and normalize APEX telecommunications missions and provider receipts across voice, SMS, SIP, PSTN, WebRTC and voicemail. Enforces source freshness, authority, idempotency inputs, provider-native receipt evidence, independent transport/contact/mission/ack state, and false-success prevention. Use when executing or verifying a telecom action."
---

# Telecommunications Execution Core

## Role
Atomic execution-semantics Skill for the APEX telecommunications domain. It does **not** place a call by itself. It verifies that a bounded mission is safe to dispatch and that provider readback supports the claimed outcome.

## Invariants
1. **Provider API success is not mission success.**
2. **Transport, contact, mission, and acknowledgement are independent state dimensions.**
3. **No stale-context dispatch.** Freshness is explicit and machine checked.
4. **No authority by implication.** The mission must carry an explicit authority assertion/action ID.
5. **No duplicate action by restart.** Stable idempotency keys are inputs to execution state.
6. **Provider-native receipt fields outrank model narration.**
7. **Voicemail ≠ acknowledgement; human answer ≠ correct unit; tracking number ≠ investigation; SMS delivered ≠ acknowledgement.**
8. **Raw provider transcripts/recordings remain immutable sources; normalization/enrichment is derivative.**
9. **Pipecat and other upstream runtimes stay clean and replaceable. GlacierEQ logic lives in adapters/sidecars/control-plane code.**

## Input contract
A JSON mission with, at minimum:
- `mission_id`, `action_id`, `idempotency_key`
- `source_freshness_at`
- `authorized: true|false`
- destination with `value` and `allowlisted`
- `channel`

Optional provider receipt JSON may be supplied for verification.

## Method
### Preflight
`HYDRATE → FRESHNESS → AUTHORITY → IDEMPOTENCY INPUT → DESTINATION → CHANNEL → READY/BLOCKED`

### Receipt verification
`NATIVE READBACK → STATE NORMALIZATION → FALSE-SUCCESS CHECK → PROVENANCE/RECEIPT GATE → VERIFIED/REPAIR`

## Output contract
`telecommunications-execution-receipt.json` containing:
- preflight status and blocking reasons;
- normalized independent state dimensions;
- false-success findings;
- provider-evidence completeness;
- conservative verified outcome;
- SHA-256 digest over the verification payload.

## Local execution
```bash
python skills/telecommunications-execution-core/scripts/run.py \
  --mission mission.json \
  --receipt provider-receipt.json \
  --output telecommunications-execution-receipt.json
```

## Validation
- stale missions fail closed;
- missing authority fails closed;
- non-allowlisted destinations fail closed;
- voicemail cannot become formal acknowledgement;
- wrong number/unit cannot satisfy a mission;
- tracking alone cannot prove investigation opened;
- SMS acceptance/delivery cannot become acknowledgement without source evidence;
- missing provider evidence yields `REPAIR`, not success.

## Does not own
- PSTN/SIP carrier implementation;
- Pipecat/LiveKit/Fonoster internals;
- legal filing authority;
- autonomous external send authority;
- Attio identity sovereignty;
- DOCKETS case truth.
