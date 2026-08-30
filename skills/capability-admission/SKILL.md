---
name: capability-admission
description: Decide whether a proposed capability may be selected for a specific mission. Use before activating a new, advanced, externally dependent, high-consequence, or strongly claimed Skill, Combo Skill, or Mega Skill.
---

# Capability Admission

## Purpose

Determine whether a capability is ready **for this mission**. This Skill owns the admission decision and its evidence; it does not claim that an unverified route is available or perform the route’s specialist work.

## Procedure

1. Identify the exact capability ID, requested mission, owner, current maturity label, and intended output.
2. Extract the route’s declared prerequisites: tools, scripts, data, access, licenses, hardware, runtime, approvals, and local validation.
3. Separate prerequisites already observed from those merely described in documentation.
4. Define the minimum evidence required to select the route and the safe fallback if it is blocked.
5. Request or invoke `resource-preflight` for every prerequisite that has not been verified in the active environment.
6. Accept the route only when the preflight, claim boundary, and mission-specific approval requirements pass. Otherwise record `candidate` or `blocked` with an owner and next action.

## Output contract

Produce `CAPABILITY_ADMISSION.md` with the capability ID, mission scope, maturity decision, observed prerequisites, gaps, evidence references, approval condition, fallback, decision owner, and review trigger.

## Local validation

The decision passes when a reviewer can tell exactly whether the capability is available now, why, what it has not proven, and the safe route if admission fails.

## Non-goals

Do not promote a capability based on a compelling description, a filename, an expected dependency, or a prior unrelated run.
