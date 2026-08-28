---
id: runtime-operations
display_name: Runtime Operations
schema: ../../schemas/combo-skill.schema.json
version: 1.0.0
status: active
---

# Runtime Operations

## Purpose and selection

Use this Combo Skill when automating native macOS applications, performing visual screen perception, or bridging local desktop runtimes to cloud connectors under quality-gated verification. Do **not** use it for pure cloud-only database querying without desktop embodiment.

## Incremental value

This Combo Skill establishes a closed-loop bridge between the native operating system desktop and distributed cloud services, verifying every GUI or process mutation against strict acceptance gates.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `computer-user-core` | Skill | Yes | Execute native desktop, window, and screen automation | System mandate or GUI action request | `computer-user-action-receipt.json` | Process executes and visual state transition is verified |
| 2 | `connector-bridge` | Skill | Yes | Route operational state and data to cloud connectors | Local action receipts and payload data | `connector-response-receipt.json` | Upstream API accepts payload and confirms persistence |
| 3 | `quality-gate` | Skill | Yes | Validate operational invariants and resource cleanup | Combined receipts and system metrics | Gate record | Zero residual zombie processes and confirmed state update |

## Ordered execution

1. **Desktop embodiment — `computer-user-core`** consumes action requests, orchestrates GUI/process automation, produces `computer-user-action-receipt.json`, and passes when screen/process transition is verified.
2. **Cloud transport — `connector-bridge`** consumes action receipts, dispatches updates to target cloud horizon (e.g. Supabase, GitHub, Cloud Storage), produces `connector-response-receipt.json`, and passes when response status is 200/201.
3. **Operational verification — `quality-gate`** consumes execution receipts and system telemetry, produces a gate record, and passes when all invariants and resource limits are satisfied.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `computer-user-core` | `connector-bridge` | Action receipts, window/process state | Dispatched payload, cloud sync confirmation | runtime operator | Native desktop action confirmed before cloud sync |
| `connector-bridge` | `quality-gate` | Cloud receipts, rate-limit metrics | Verified operational gate record | quality auditor | Cloud transport confirmed and zero errors recorded |

## Evidence, risks, and state

The Combo must record all screen dimensions, process PIDs, API response status codes, and latency numbers in its evidence register. Clean up all temporary screenshots and lockfiles after execution.

## Quality gates

The Combo is complete only when native macOS action executes cleanly, cloud connectors register state persistence, and `runtime-operations-record.md` is emitted.

## Compound output

**Artifact:** `runtime-operations-record.md`

**Ready for Mega Skill integration when:**

1. Native desktop action successfully executes with zero process hangs.
2. Cloud connectors confirm synchronized state across local and remote horizons.
3. Quality gate verifies complete resource cleanup and telemetry integrity.
