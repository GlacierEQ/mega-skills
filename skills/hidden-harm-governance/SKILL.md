---
name: hidden-harm-governance
description: "Counter-engineer governance harms: convert false HARD-GATEs, approval theater, GATE DENIED permission language, token soft-caps, and commit/push pauses into quality pitstops (level-ups) that enrich and continue. Keep only reserved irreversible boundaries as hard stops."
---

# Hidden Harm — Governance as Pitstop

## Mission

Imported skills spend enormous force on **stopping**. That force is useful. This skill keeps the force and changes what it buys.

A hard halt is not a permission gate. It is a **pitstop**: a quality level that upgrades design clarity, plan coherence, claim strength, diff integrity, or remote readback — then the mission continues.

## Polarity law

```text
FALSE HARD-HALT     →  QUALITY PITSTOP (enrich + continue)
GATE DENIED label   →  claim-strength debt + continue authorized work
WAIT FOR APPROVAL   →  tighten the quality dimension, then execute
TOKEN % / DEPTH STOP→  reallocate spend, keep mission moving
COMMIT/PUSH PAUSE   →  verify diff / push + readback (ordinary engineering)
RESERVED BOUNDARY   →  HARD_BOUNDARY (only true stop)
```

Executable surface: `scripts/gate_polarity.py` via `operator_mission_kernel` operation `gate_polarity`.

Aligned with `apex-boot-core` enrichment transitions and `epistemic-gate` claim-strength model (tiers are not authorization).

## Pitstop transitions

| Telemetry | Transition |
|---|---|
| `PASS` | `VALIDATED_LEVEL_UP` |
| `WARN` | `ENRICH_WITH_UNCERTAINTY` |
| `FAIL` | `LOCALIZE_REPAIR_REROUTE_LEVEL_UP` |
| `MISSING` | `DISCOVER_ACQUIRE_LEVEL_UP` |
| `DRIFT` | `RECONCILE_ENRICH_LEVEL_UP` |
| `THEATER` | `STRIP_PERMISSION_LABEL_LEVEL_UP` |

A pitstop changes route quality, not Operator authority. Only the Operator changes mission or project direction.

## Reserved hard boundaries (not pitstops)

Keep hard-stop polarity for:

- court filing / outbound legal service
- production deploy
- unbudgeted capital spend
- destroying primary evidence
- irreversible delete / force-push history rewrite
- MFA, signature, or Operator-name public communication without template

These match `AGENTS.md` Strict Human Approval Boundary. Continue all independent fronts while that local boundary is open.

## False halts → quality dimensions

| Former halt | Quality dimension | Pitstop |
|---|---|---|
| Design HARD-GATE | design_clarity | clarify assumptions, then implement |
| Orch GATE 1 | plan_coherence | tighten plan slice, then implement |
| Orch GATE 2 / batch wait | diff_integrity / batch_verification | verify, then commit/continue |
| Remote-push pause | remote_readback | push and read back |
| Token / depth menu stop | spend_efficiency | reallocate, keep moving |
| GATE DENIED as permission | claim_strength | record verification debt, continue |
| Support-only rejection of requested deliverable | deliverable_fidelity | requested deliverable *is* the outcome |

## HARD-PITSTOP contract

<HARD-PITSTOP>
When the Operator has already requested implementation, execution, continuation, commit, push, or a finished deliverable of reversible engineering:

- Do NOT convert design review, plan review, commit check, install check, depth menu, or epistemic tier into a permission stop.
- Take the pitstop: raise the named quality dimension, emit the enrichment transition, continue the mission.
- Strip permission labels (`HARD-GATE`, `GATE DENIED`, `authorized for execution`, `delivery blocked`) from verification language.
- Verify with readback. Preserve lineage. Keep reserved irreversible boundaries as the only hard stops.

Use the same absolute force those imported skills used to halt — spend it on quality level-up, not on blocking.
</HARD-PITSTOP>

## Procedure

1. Recover Operator semantic lock (`BUILD` / `EXECUTE` / `CONTINUE` / `MAXIMUM`) and whether a finished deliverable was requested.
2. Classify the candidate halt: reserved boundary vs false halt.
3. Call `gate_polarity` with the proposed gate text / markers / telemetry.
4. If `QUALITY_PITSTOP`, perform the pitstop action and continue — do not ask for re-approval of already-authorized work.
5. If `HARD_BOUNDARY`, pause only that effect and continue independent fronts.
6. Never invent a new permission ladder. This skill turns false ladders into service bays.

## Composition

- Context / Operator semantics → also compose `hidden-harm-context`
- GitHub / push / CI → also compose `hidden-harm-github`
- Connectors / MCP → also compose `hidden-harm-connectors`
- Legal / evidence → also compose `hidden-harm-casebuild`
- General remainder → `hidden-harm-cross-domain`

Route through `power-skill` and `casey-operator-execution-kernel`. This specialist owns governance→pitstop conversion.

## Success

Success is not a softer agent and not a blunter one. Success is an agent that treats every former ceremonial halt as a quality level — faster out of the bay, stronger after the stop — while remaining unable to cross a true irreversible boundary by accident.
