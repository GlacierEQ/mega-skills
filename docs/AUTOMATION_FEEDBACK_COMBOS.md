# Automation and Feedback Combo Batch

## Design objective

This batch creates **control loops**, not uncontrolled background agents. Each Combo closes an explicit loop—signals to decision, approved intent to a guarded run, or evidence to a governed improvement proposal—while preserving human approval at external-effect boundaries.

| Combo Skill | Loop it closes | Primary output | Does not do |
|---|---|---|---|
| `signal-to-decision-loop` | Observe → assess → plan → gate | `SIGNAL_DECISION_RECORD.md` | Execute a change or poll continuously by default |
| `guarded-automation-loop` | Admit → preflight → execute → verify → recover | `GUARDED_RUN_RECORD.md` | Activate external effects without route and approval checks |
| `evidence-to-evolution-loop` | Observe → calibrate → improve → validate → register | `CAPABILITY_EVOLUTION_PROPOSAL.md` | Self-modify an active capability or promote a proposal without review |

## Selection rules

`signal-to-decision-loop` is used when new data, a failure, or a scheduled review might require a future decision. It produces a decision-ready artifact, not a change. `guarded-automation-loop` is used only after an approved automation architecture exists and its requirements are available for mission-specific preflight. `evidence-to-evolution-loop` is used when repeated evidence justifies a change proposal for a Skill, Combo Skill, Mega Skill, documentation contract, or test suite.

All three routes must use `capability-readiness` before advanced execution is admitted. If the environment, access, data, or claim boundary is not verified, the loop returns a blocked record and safe next action.

## Trigger discipline

The Combo contract must separate **a detected condition** from **an execution mechanism**. For a durable implementation, the user still chooses an appropriate schedule, event, or persistent service architecture after assessing frequency, latency, determinism, data source, management need, and resource requirements. A Combo Skill may define the logic and evidence contract, but it must not silently create a schedule, poll a service, send a message, mutate a repository, or invoke an external API.

## Feedback discipline

Each loop records the observed signal, decision, action authority, result, evidence, residual uncertainty, and next review trigger. Failures route to a named owner with a bounded fallback. Learning accumulates only through evidence-backed proposals, never by overwriting prior state or treating an isolated result as a universal rule.
