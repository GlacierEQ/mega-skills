# Autonomous Engineering Pipeline Simulation Contract

The repository harness models orchestration behavior without touching external services, production systems, or real repositories. It is a deterministic integration simulation, not proof that a real project’s code, scanners, profilers, or toolchains are correct.

## Scenarios

| Scenario | Expected terminal state | What it proves |
|---|---|---|
| `happy` | `VERIFIED` | Core specialist routing, handoffs, quality gate, approval, and release |
| `security-block` | `BLOCKED` | A critical security finding prevents quality and release evidence |
| `approval-required` | `ESCALATED` | Release stops at the explicit irreversible-mutation boundary |
| `tower-route` | `VERIFIED` | Tower evidence steps preserve the mandated order |
| `handoff-recovery` | `VERIFIED` | A failed handoff is recorded, recovery is explicit, and execution resumes |
| Invalid scenario | Non-zero process exit | Unknown routes fail closed |

## Run the simulation

From the repository root:

```bash
python skills/autonomous-software-engineering/scripts/run_pipeline_simulation.py --scenario happy
python -m unittest discover -s skills/autonomous-software-engineering/tests -v
```

The JSON output contains the mission ID, terminal state, current stage, approval status, evidence map, handoffs, events, and blocked reason. Assertions should verify state transitions and evidence, not just process exit codes.

## Extension rules

When adding a scenario, specify its expected terminal state, route, failure or recovery condition, and the evidence that proves the condition. Keep scenarios deterministic and side-effect free. Do not add live network calls, credentials, production paths, or destructive operations to the simulation. Add a test for both the intended route and the relevant rejection or recovery route.
