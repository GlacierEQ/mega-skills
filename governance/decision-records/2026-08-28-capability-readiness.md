# Capability Readiness Before Advanced Route Selection

## Context

The repository now contains specialized Skills and Mega Skills whose descriptions reference external scripts, substantial data volumes, named models, credentials, operational estates, and strong outcome claims. The hierarchy schema confirms identifiers and composition fields, but it cannot establish that those dependencies exist or that the stated outcomes have been validated.

## Decision

Add a common readiness layer composed of three atomic Skills: `capability-admission`, `resource-preflight`, and `claim-calibration`. Add the `capability-readiness` Combo Skill and make it conditionally selectable by Far Away Party when an advanced route needs dependency, maturity, or claim-boundary verification.

## Consequences

Existing specialized entries are not downgraded automatically because that would require package-specific evidence review. However, new or materially changed advanced routes must pass readiness before being represented as active for a particular mission. The readiness record creates the evidence needed for maintainers to later classify each package deliberately.

## Review trigger

Review this decision once the first two advanced capability families have completed a concrete preflight and their maintainers have supplied dependency and validation evidence.
