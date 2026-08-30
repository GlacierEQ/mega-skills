---
name: long-horizon-core
description: 'The 7-stage resilient long-horizon operating loop: mission-contract
  -> roadmap-builder -> evidence-register -> context-capsule -> work-packet -> quality-gate
  -> handoff-record. Generates and maintains the 5 durable state files (MISSION.md,
  ROADMAP.md, CONTEXT.md, EVIDENCE.md, HANDOFF.md) for zero-drift execution.'
version: 0.1.0
---

# 🔁 Long-Horizon Core Combo-Skill

The foundational 7-stage operating loop that enables multi-agent swarms and autonomous systems to complete complex, multi-phase missions with zero context drift and guaranteed lossless resumption.

## The 7-Stage Execution Loop

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ 1. MISSION      │  ──►  │ 2. ROADMAP      │  ──►  │ 3. EVIDENCE     │
│ Boundary & Scope│       │ Phases & Gates  │       │ Proof & Claims  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                                             │
┌─────────────────┐       ┌─────────────────┐       ┌────────┴────────┐
│ 6. QUALITY GATE │  ◄──  │ 5. WORK PACKET  │  ◄──  │ 4. CONTEXT      │
│ Validate Proof  │       │ Bounded Chunk   │       │ Lean State      │
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐
│ 7. HANDOFF      │  ──► Next Phase or Safe Resumption
│ Exact State     │
└─────────────────┘
```

## Stage Contracts

| Stage | Procedure | Input | Output | Verification |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `mission-contract` | User request | `MISSION.md` | Scope, exclusions, approvals explicit |
| **2** | `roadmap-builder` | `MISSION.md` | `ROADMAP.md` | Dependencies and gates explicit |
| **3** | `evidence-register` | Raw files & tests | `EVIDENCE.md` | Every claim mapped to physical proof |
| **4** | `context-capsule` | State & evidence | `CONTEXT.md` | Actionable capsule (<200 lines) |
| **5** | `work-packet` | Current chunk | Work Packet | Bounded owner, task, and test harness |
| **6** | `quality-gate` | Artifact & test | Gate Record | Rejects unverified completion |
| **7** | `handoff-record` | Gate outcome | `HANDOFF.md` | Deterministic resumption point |

## Invariant Laws
1. **Never Advance on Failure**: If Stage 6 (Quality Gate) fails, return to Stage 5 (Work Packet). Never advance to Stage 7.
2. **Context Compaction**: Intermediate chatter is discarded; only `CONTEXT.md` and `HANDOFF.md` persist.
