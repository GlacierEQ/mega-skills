---
name: mastermind
description: "Operating inside the Mastermind mission-control runtime (MASTERMIND_HOME or the Mastermind checkout). Use when wiring lanes, appending to the receipt chain, configuring identity policy, adding adapters, seeding quality processors, or running the test suite. The canonical APEX Sovereign Runtime lives here."
---



# Mastermind Skill

Mission-control runtime with SHA-256 linked receipt chains, strict identity
gating, and lane-based routing. Canonical implementation of the
**APEX Sovereign Runtime** doctrine.

**Do not duplicate runtime doctrine here — load `apex-sovereign-runtime` first.**

## Project Layout

| Path | Purpose |
|------|---------|
| `__main__.py` | CLI entry: `python -m mastermind` |
| `runtime/spine.py` | `MastermindRuntime` — main orchestrator |
| `runtime/identity.py` | Component identity, signing, verification |
| `runtime/receipt.py` | Append-only SHA-256 linked receipt ledger |
| `runtime/config.py` | Runtime configuration (env + yaml) |
| `lanes/` | Lane routing: github, portfolio, nasa, vercel, … |
| `adapters/` | External service adapters (read-only) |
| `tower/` | Tower governance integration |
| `identity/` | Identity providers and trust roots |
| `receipts/` | Receipt storage + audit trail |
| `tests/` | Unit + integration tests |

## Key Commands

Prefer `MASTERMIND_HOME` (portable). Legacy `/root/projects/mastermind` is an optional donor only.

```bash
# Set MASTERMIND_HOME to the Mastermind checkout, then enter it.
export MASTERMIND_HOME="${MASTERMIND_HOME:-$PWD}"
cd "$MASTERMIND_HOME"

# Maximize mesh + seed Kanban quality processors
python3 maximize_mastermind.py

# Health / execute / chain (module CLI)
python -m mastermind health
python -m mastermind execute "deploy portfolio" --component portfolio --capability deploy
python -m mastermind chain
python -m mastermind receipts

# Focused reconnect proofs
python3 -m unittest tests.test_paths_portable tests.test_quality_processor -v
```

Compose `pro-mastermind-quality-processors` when restoring unplugged power or cruising Kanban×calibrator workers across the estate.

## Hard Rules (Non-Negotiable)

1. **Identity is strict by default** (`identity_strict=True`).
   - Unknown components are rejected at the gate. No silent acceptance.
   - To admit a new component: register it in `identity/` with a signed
     manifest, then re-verify. **Never** flip `identity_strict=False` to
     "just make it work" — that's an audit failure.

2. **Receipts are immutable once appended.**
   - Each receipt links to the previous via SHA-256.
   - Never edit, delete, or reorder a receipt. Append a *corrective* receipt
     instead. The chain is the audit trail.

3. **Lanes own their domain.**
   - `lanes/github.py` knows about GitHub. `lanes/portfolio.py` knows about
     the portfolio. Don't reach into another lane's data — go through the
     lane's public API.

4. **All state-changing actions append a receipt** — reads do not.
   - If your action changes state and produces no receipt, it didn't happen.

## Receipt Format (Quick Reference)

```json
{
  "seq": 42,
  "prev_hash": "ab12...",
  "timestamp": "2026-08-27T18:34:30-10:00",
  "component": "portfolio",
  "capability": "deploy",
  "intent": "deploy portfolio v1.2",
  "actor": "casey@glaciereq",
  "params": {"target": "production"},
  "result": "ok",
  "hash": "9f3c..."
}
```

The `hash` covers all fields above; `prev_hash` chains to the previous
receipt. Verifying the chain re-hashes and re-links; a mismatch means
tampering or corruption.

## Lane Authoring (How to Add a Lane)

1. Create `lanes/<name>.py` with a class implementing the lane protocol.
2. Register it in `lanes/__init__.py` and `runtime/spine.py`.
3. Add a test in `tests/test_<name>_lane.py` covering happy path + one failure.
4. Add a capability manifest in `identity/` with the lane's signing pubkey.
5. Run `python -m mastermind health` to confirm registration.

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Flipping `identity_strict=False` to bypass a gate | critical | **Never.** Register the component properly or it doesn't run. |
| Editing a receipt in the chain | critical | **Appends only.** Use a corrective receipt. |
| Lane reaching into another lane's storage | high | **Go through the lane's public API.** Cross-lane coupling is a maintenance and audit hazard. |
| Action without a receipt | critical | **Every state change appends a receipt** — no exceptions, no "we'll log it later." |
| Trusting `actor` field without signature verification | critical | **Verify the signature** against the identity registry. The `actor` string is untrusted input. |
| Long receipt chains slowing verification | medium | **Checkpoint snapshots** are allowed (in `receipts/snapshots/`) but the full chain must remain queryable. |

## Related Skills

- `apex-sovereign-runtime` — full runtime doctrine (load this first)
- `ai-agents-architect` — agent topology, planning, tools
- `clean-code` — pragmatic Python standards
- `security-review` — for any lane handling auth, secrets, or external services
- `architecture` — for ADR-shaped decisions on lane boundaries
