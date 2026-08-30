---
name: apex-aerospace-sim
description: 'Mega Skill: apex-aerospace-sim. End-to-end sovereign mission system.'
---

# APEX Aerospace Simulation Mega Skill

## Mission

Orchestrate high-fidelity aerospace simulation campaigns spanning orbital mechanics propagation, Lambert transfer targeting, cryogenic propellant boil-off, and launch countdown sequencing across SpaceX flight software repositories.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `long-horizon-core` | `aerospace-mission-simulation` when trajectory or boil-off models are tested | Manages multi-vehicle mission profiles, delta-v budgets, and orbital safety gates. |
| `long-horizon-core` | `automation-control` when automated simulation pipelines or hardware monitors are active | Automates telemetry ingestion, real-time sensor polling, and countdown abort triggers. |

## Route algorithm

1. Begin the aerospace mission with `long-horizon-core` and load mission parameter contracts.
2. Select `aerospace-mission-simulation` to solve Lambert targeting and propagate orbital elements.
3. Evaluate thermodynamic cryogenic boil-off models to ensure tank pressure safety.
4. Select `automation-control` if hardware-in-the-loop or automated test harnesses are running.
5. Require 100% green unit assertions across `spacex-orbital-mechanics` and `spacex-cryogenics`.
6. Reconcile telemetry records, delta-v budgets, and conjunction assessments into `EVIDENCE.md` and deliver final mission package.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` maintain immutable mission state across orbital simulation phases.
