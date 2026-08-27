---
id: aerospace-mission-simulation
display_name: Aerospace Mission Simulation
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Aerospace Mission Simulation

## Purpose and selection

Use this Combo Skill when aerospace flight dynamics, orbital transfer maneuvers, or cryogenic propellant simulations must be validated across flight software repositories. Do **not** use it for general non-aerospace software tasks.

## Incremental value

This Combo Skill combines mission parameter bounds with high-order orbital integration and cryogenic boil-off thermodynamics, emitting an evidence-backed telemetry verification record with delta-v budgets and collision conjunction assessments.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set flight profile and orbital target criteria | Mission mandate | `MISSION.md` | Target orbital parameters are explicit |
| 2 | `aerospace-trajectory-core` | Skill | Yes | Propagate orbits, solve Lambert, and compute boil-off | `MISSION.md` and state vectors | `aerospace-trajectory-telemetry.json` | Energy and momentum conservation verified |
| 3 | `quality-gate` | Skill | Yes | Verify aerodynamic and thermal limits | Telemetry logs | Gate record | Conjunction risk below threshold; tests pass |

## Ordered execution

1. **Mission boundary — `mission-contract`** consumes mission requests and target orbit parameters, produces `MISSION.md`, and passes when flight constraints and target state vectors are explicit.
2. **Trajectory propagation — `aerospace-trajectory-core`** consumes `MISSION.md`, produces `aerospace-trajectory-telemetry.json`, and passes when Lambert solvers and thermal equations converge.
3. **Flight safety gate — `quality-gate`** consumes telemetry logs and thermal limits, produces a gate record, and passes when orbital mechanics test suites pass 100% green.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `aerospace-trajectory-core` | Target orbit, state vectors, propellant mass | Verified telemetry packet and trajectory vectors | flight dynamics owner | Flight constraints and parameters are explicit |
| `aerospace-trajectory-core` | `quality-gate` | Telemetry logs, boil-off curves, delta-v | Verified gate record | safety owner | 100% test assertions pass with zero limit violations |

## Evidence, risks, and state

The Combo must record all state vectors, delta-v budgets, boil-off curves, and conjunction probabilities in its evidence register. It must not bypass structural or aerodynamic thermal safety limits. Update active state after each flight phase.

## Quality gates

The Combo is complete only when all orbital integration tests pass with numerical precision, mechanical energy is conserved, and `aerospace-simulation-record.md` is emitted.

## Compound output

**Artifact:** `aerospace-simulation-record.md`

**Ready for Mega Skill integration when:**

1. Delta-v budget and orbital transfer vectors are verified.
2. Cryogenic boil-off pressure curves remain within structural limits.
3. Collision conjunction probabilities are evaluated.
