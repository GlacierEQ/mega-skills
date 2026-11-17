---
name: team-delivery
description: "Dispatch a named team, keep its board/merge-gate alive, and produce an E0 receipt (sha256-chained) when the team finishes. Use when executing a mission-team that must produce a deliverable."
version: 0.1.0
author: GlacierEQ · ECC · user
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [team-delivery, kanban, receipt, sha256, mission-team]
    related_skills: [team-builder, team-agent-orchestration, apex-orchestration, ws-verify]
---

# Team Delivery

Dispatch an agent team, run it to a deliverable, and hand back an E0 receipt. This is
the production path; `team-builder` selects roles, `team-agent-orchestration` runs the
board, `ws-verify`/`temapi` verify the output.

## When to use

- The task spans more than one specialist role and must produce a fused, receipt-verified
  artifact.
- You need a Kanban card + owner + merge gate instead of a free-form team chat.
- A mission explicitly requires a `l2_proof: true` receipt chaining.

## Workflow (intent → receipt)

1. **Shape the board** (`team-builder` mode) — pick owners + roles with a merge gate.
2. **Write the canvas** `teamagent/<mission>/CANVAS.md` — mission, acceptance, risks,
   artifact list, team identity (no cross-contamination).
3. **Dispatch** via `bin/team-delivery run` — the dispatcher writes a `teamreceipt.json`
   before starting, appends post-run verification, and emits
   `teamreceipt.receipt.json` + `receipt_sha256` chain.
4. **Verify** — `bin/team-delivery verify <receipt>` re-runs the mission's
   `ws-verify` + pytest + `l2_proof: true` check.
5. **Fuse** — `team-agent-orchestration` merge-gate; the receipt is the gate token.

## Contract (receiver must be able to replay)

```jsonc
{
  "schema": "glaciereq.team-delivery.receipt.v1",
  "mission": "<mission slug>",
  "team": ["role:agent", ...],
  "state": "pending|running|merged|rejected",
  "artifacts": ["path/to/artifact"],
  "l2_proof": true,
  "receipt_sha256": "<64-hex sha256 of the receipt file>",
  "parent_mission_id": "<mission id>",
  "started_at": "<RFC3339>",
  "completed_at": "<RFC3339 or null>"
}
```

## Rules

- **No un-wired hop.** Every team must pass through `bin/team-delivery` and end in a
  receipt with `l2_proof: true`.
- **Receipts are append-only.** Never overwrite a received artifact; write a new chain.
- **No secrets in receipts.** Receipts carry roles + paths + hashes, never keys/tokens.
- **Merge gate.** A team may not leave `teamagent/` until its receipt is verified
  green (fail-closed: unverified receipt = BLOCKED).
