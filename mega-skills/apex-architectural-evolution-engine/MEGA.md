# APEX Architectural Evolution Engine

## Mission

Continuous autonomous codebase modernization: diagnoses architectural bottlenecks, designs formal Architecture Decision Records, conducts clean refactoring with AST self-healing, and enforces Google Senior Staff engineering invariants across the estate.

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
| `architectural-refactoring-engine` | `capability-readiness` | Coordinates end-to-end execution of architectural-refactoring-engine with mission-level state gates. |
| `long-horizon-core` | `closed-loop-code-repair` | Dynamically activates closed-loop-code-repair based on mission requirements. |
| `long-horizon-core` | `upstream-fork-harmonization` | Dynamically activates upstream-fork-harmonization based on mission requirements. |
| `long-horizon-core` | `recon-and-map` | Dynamically activates recon-and-map based on mission requirements. |

## Route algorithm

1. Initialize mission state with `long-horizon-core` and load mission boundary parameters.
2. Evaluate `capability-readiness` for all required and conditional combo routes.
3. Execute primary pipeline via `architectural-refactoring-engine`.
4. Conditionally dispatch specialist combos based on runtime risk flags and telemetry.
5. Compile final verified deliverable into `ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md` and persist immutable state.

## Durable state

`MISSION.md, ROADMAP.md, CONTEXT.md, EVIDENCE.md, HANDOFF.md` maintain durable mission state across sprints and server restarts.
