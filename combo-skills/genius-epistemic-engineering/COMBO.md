---
id: genius-epistemic-engineering
display_name: Genius Epistemic Engineering
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Genius Epistemic Engineering

## Purpose and selection

Use this Combo when a Genius entity must think and build: classify knowledge, authorize action on the L0–L6 ladder, then engineer with helix-pro-code and refuse completion without fresh proof. Do **not** use it to dump coding catalogs or to skip the Genius-Mastery kernel; route forging to `genius-entity-forge`.

## Incremental value

This Combo does not copy epicenter, epistemic-gate, helix, or verification methods. It orders them so Genius cannot treat L0 sight as L2 fact, cannot code without helix law, and cannot say done without a live command receipt.

## Member contract

| Order | Member | Kind | Required | Role | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `epicenter` | Skill | Yes | Tag claims L0/L1/L2 before action | Role brief or proposed claim | Layer-tagged claim set | Every fact is L2 or tagged |
| 2 | `epistemic-gate` | Skill | Yes | Authorize only L2+ local / L5+ enterprise | Layer-tagged claims | `epistemic-verification-receipt.json` | Below-L2 actions denied |
| 3 | `helix-pro-code` | Skill | Yes | Alpha/Omega engineering for authorized work | Gate receipt + coding mandate | Engineering delta + carryover check | Gap analysis then verify-readback |
| 4 | `verification-before-completion` | Skill | Yes | Block done-claims without fresh command output | Engineering delta | Verification receipt | Claim text matches this-turn output |

## Ordered execution

1. **Know — `epicenter`** consumes the brief, produces L0/L1/L2-tagged claims. Untagged “facts” fail closed.
2. **Authorize — `epistemic-gate`** accepts only tagged claims, produces the epistemic receipt. L0/L1 never authorizes mutation.
3. **Engineer — `helix-pro-code`** accepts only an authorized receipt, produces the engineering delta. Load TDD or systematic-debugging only when that step needs them; do not dump the catalog.
4. **Prove — `verification-before-completion`** accepts the delta, produces a verification receipt from a command run in this turn. Failure returns to helix, never a fake PASS.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `epicenter` | `epistemic-gate` | Layer-tagged claims | Epistemic receipt | epistemologist | Untagged claims do not enter the gate |
| `epistemic-gate` | `helix-pro-code` | L2+ authorization | Engineering delta | engineer | Below-L2 work is not coded |
| `helix-pro-code` | `verification-before-completion` | Delta + intended claim | Fresh command receipt | reviewer | “Done” without this-turn output is a FAIL |

## Evidence, risks, and state

Record epistemic tier, helix carryover check, and the verification command with exit code. Do not paste kernel anatomy. Mega firewall still requires human approval for `external_mutation`.

## Compound output

**Artifact:** `genius-epistemic-engineering-receipt.md` (layers + gate + helix delta + verification).
