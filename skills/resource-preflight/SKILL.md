---
name: resource-preflight
description: Verify the environment, dependencies, access, data, approvals, and validation resources required by a capability before it is selected. Use when a route names tools, scripts, models, datasets, credentials, services, hardware, or runtime assumptions.
---

# Resource Preflight

## Purpose

Turn declared prerequisites into observed environment facts. This Skill owns availability, version, permission, and suitability checks; it does not install, configure, or invoke unapproved resources.

## Procedure

1. Build a prerequisite inventory from the selected capability and mission contract.
2. For each item, record its type, expected identifier/version, source of truth, owner, required permission, and verification method.
3. Check only authorized, non-destructive availability signals: existence, version, access status, scope, quota, data classification, and policy fit.
4. Classify each item as `verified`, `missing`, `incompatible`, `restricted`, `expired`, or `not-applicable`.
5. Identify a safe fallback for every non-verified required item; do not silently substitute another tool, data source, or access path.
6. Record the exact preflight time, environment, evidence, and expiry/recheck condition.

## Output contract

Produce `RESOURCE_PREFLIGHT.md` with a prerequisite table, observed status, evidence link, owner, fallback, and a final `ready`, `conditional`, or `blocked` result.

## Local validation

The preflight passes when every required prerequisite has a current observed status, missing items have safe fallbacks, and the route’s claimed output does not exceed verified resources.

## Non-goals

Do not install dependencies, reveal secrets, access restricted data, or treat configuration text as proof that a dependency works.
