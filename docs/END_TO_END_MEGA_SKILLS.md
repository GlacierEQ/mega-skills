# End-to-End Mega Skill Batch

## Operating boundary

These Mega Skills coordinate multiple Combo Skills across a whole mission. They are **autonomous in planning, evidence reconciliation, route selection, quality control, and recovery**, but they do not bypass approvals, activate persistent processes, or represent external effects as completed without observed evidence. Every advanced route starts with `capability-readiness`; every external-effect route requires a separate mission-specific approval and a guarded execution contract.

| Mega Skill | Mission shape | Required foundation | Conditional routes | Final mission artifact |
|---|---|---|---|---|
| `apex-adaptive-operations` | Observe changing conditions and coordinate a bounded operational response | `long-horizon-core` | `capability-readiness`, `signal-to-decision-loop`, `guarded-automation-loop`, `automation-control`, `evidence-to-evolution-loop` | `ADAPTIVE_OPERATIONS_MISSION_RECORD.md` |
| `apex-capability-foundry` | Convert proven recurring work into a review-ready skill-system increment | `long-horizon-core` | `capability-readiness`, `recon-and-map`, `signal-to-decision-loop`, `evidence-to-evolution-loop`, `skill-forge` | `CAPABILITY_FOUNDRY_MISSION_RECORD.md` |
| `apex-safe-change-orchestrator` | Inspect, decide, repair or change, verify, and preserve a recoverable repository change record | `long-horizon-core` | `capability-readiness`, `recon-and-map`, `signal-to-decision-loop`, `closed-loop-code-repair`, `guarded-automation-loop` | `SAFE_CHANGE_MISSION_RECORD.md` |

## Route model

```text
mission contract → long-horizon durable state
                       │
                       ▼
              capability-readiness
                       │
     ┌─────────────────┼──────────────────┐
     ▼                 ▼                  ▼
signal → decision   guarded action     evidence → evolution
     │                 │                  │
     └────────── quality / evidence / handoff ──────────┘
                       │
                       ▼
          Mega-level integration artifact
```

## Selection principles

Select the smallest capable Mega route. A Mega Skill earns its layer only if it coordinates at least two distinct Combos, adds mission-wide sequencing and recovery, and emits a compound record that cannot be produced by one Combo alone. It must not duplicate Combo procedures.

## Mega Skill Forge

The reusable `mega-skill-forge` package turns this proven process into a constrained authoring workflow. It inventories real lower-layer evidence; determines whether a Mega Skill adds genuine integration value; selects resolved Combo dependencies; writes the mission contract and registry entry; validates the complete graph; and packages a reviewable change. It refuses a proposal that has fewer than two Combos, unresolved dependencies, a duplicated Combo procedure, unsupported operational claims, or missing recovery and approval boundaries.
