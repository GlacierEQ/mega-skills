# Decision Record — Casebuild Mesh Layering

**Date:** 2026-09-01  
**Status:** Proposed

## Decision

Add `casebuild-mesh-organization` as an atomic Skill and `apex-casebuild-mesh` as a Mega Skill. Activate the existing `apex-always-on-core` for the initial casebuild mission through durable mission-state artifacts rather than copying or modifying its contract.

## Rationale

The organization procedure is independently useful and has its own trigger, artifact, and local validation, so it belongs at the Skill layer. Full case building conditionally routes multiple existing Combos across a long horizon and owns durable integration state, phase gates, and resumption, so it belongs at the Mega layer.

The new Mega Skill reuses existing Combo IDs. It adds cross-system case graph integration, source/derivative boundaries, reconciliation, attorney-review routing, and completion gates without copying lower-layer methods.

## Compatibility

- No existing Skill, Combo, Mega Skill, or registry ID changes.
- Existing legal/forensic capabilities remain peers and can enrich the mission.
- `apex-always-on-core` remains unchanged and supplies continuity through the mission workspace.
- External mutations, legal filings, strategic decisions, and production release remain human-controlled.

## Validation required

- Validate Skill frontmatter and independent trigger.
- Confirm all referenced Combo IDs exist.
- Validate registry paths and unique IDs.
- Run hierarchy validation and repository tests before merge.
