---
id: genius-entity-forge
display_name: Genius Entity Forge
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Genius Entity Forge

## Purpose and selection

Use this Combo when a Genius entity must be named, synthesized, validated, and receipted through the Genius-Mastery kernel. Do **not** use it for ordinary skill authoring; route to `skill-forge` instead.

## Incremental value

This Combo does not copy Genius-Mastery methods. It orders kernel execution with evidence and a quality gate so a Mega can route a forge mission without replaying CLI folklore.

## Member contract

| Order | Member | Kind | Required | Role | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `genius-mastery` | Skill | Yes | Run kernel name/validate/doctor/synthesize | Role brief or repo path | Kernel receipt | `genius validate` PASS |
| 2 | `evidence-register` | Skill | Yes | Trace claims to VECTOR/CLAIMS | Kernel receipt | `EVIDENCE.md` | Claims map to evidence |
| 3 | `quality-gate` | Skill | Yes | Accept only kernel-backed output | Evidence + criteria | Gate record | Pytest or validate green |

## Ordered execution

1. **Kernel — `genius-mastery`** consumes the role or repo, produces a Genius-Mastery receipt.
2. **Trace — `evidence-register`** accepts only that receipt, produces `EVIDENCE.md`.
3. **Gate — `quality-gate`** accepts evidence, produces a gate record; failure returns to the kernel, never silent advance.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `genius-mastery` | `evidence-register` | validate/doctor/pytest receipt | Claim-linked evidence | kernel operator | Kernel FAIL does not enter the register as PASS |
| `evidence-register` | `quality-gate` | EVIDENCE.md | Gate record | reviewer | Missing VECTOR/CLAIMS fails the gate |

## Evidence, risks, and state

Record kernel version, pytest count, and repo path. Do not copy exhibits or secrets onto public runners. Update family INDEX only after the gate.

## Compound output

**Artifact:** `genius-entity-forge-receipt.md` (kernel receipt + evidence + gate).
