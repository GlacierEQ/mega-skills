---
name: strong-smart-routing-kernel
description: Enforce strongest-intelligent-fit capability routing without weakening authorization, evidence, or human-control boundaries.
---

# Strong-Smart Routing Kernel

## Purpose

This is an executable routing and dispatch gate for the operator invariant:

> **STRONG AND SMART, NOT SMALL AND MINIMAL.**

It supplements—not replaces—the Casey Operator Execution Kernel. The Casey kernel remains authoritative for mission selection, semantic locks, corrections, authority, and completion. This skill owns the measurable capability-fit decision used inside that authority envelope.

## Use when

- A mission has multiple plausible tools, skills, connectors, models, or execution plans.
- A default route is attractive mainly because it is smaller, faster to describe, or easier for the assistant.
- The operator requests MAXIMUM, strongest, best-of-all-worlds, power-skill, exhaustive, longest-strongest, or mission-complete execution.
- A proposed stack must prove that it has sufficient evidence, resilience, coverage, composability, and verification depth.

## Do not use when

- The user explicitly requests a constrained quick answer and the constraint does not conflict with safety or required rigor.
- The candidate set is not comparable or lacks enough evidence to score honestly; gather evidence first.
- The routing decision would bypass approval, authorization, privacy, security, legal-review, or human-control gates.

## Executable contract

`skill.py` accepts a mission profile and candidate routes, computes a power-fit score, identifies dominated routes, and emits one of:

- `SELECTED`: strongest coherent authorized route wins.
- `BLOCKED`: no candidate satisfies hard gates.
- `REVIEW_REQUIRED`: top candidates are too close or evidence is insufficient for a defensible automatic choice.

Hard gates are never traded for capability: authorized scope, required approvals, evidence floor, safety boundary, and human-control points.

Among candidates that pass hard gates, maximize mission coverage, intelligence fit, evidence strength, verification depth, resilience, composability, strategic leverage, and execution readiness. Cost and complexity are constraints and tie-breakers, never an automatic reason to choose a weaker route.

## CLI

```bash
python skills/strong-smart-routing-kernel/skill.py evaluate --input route-candidates.json
python skills/strong-smart-routing-kernel/skill.py evaluate --input route-candidates.json --output POWER_FIT_ROUTE.json
```

## Invariants

- Never translate MAXIMUM into an MVP, proof of concept, or convenience-first route.
- Never reward tool-count theater; unused or redundant capability receives no value.
- Never reduce safety, authorization, evidence, privacy, or human control to inflate power.
- Never claim a consequential external effect without provider-native readback.
- Preserve rejected strong alternatives and reasons so routing can be audited and resumed.

## Local validation

```bash
python -m unittest tests/test_strong_smart_routing_kernel.py
```
