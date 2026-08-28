# Capability Readiness and Claim Discipline

## Why this control exists

A Mega Skills repository may describe ambitious future capability, but a description is not evidence that the needed software, data, access, compute, permissions, or validation environment exists. A capability is **active** only when an operator can satisfy its prerequisites and reproduce its named local validation. Until then, it is a candidate route with stated assumptions.

This document introduces a reusable readiness route rather than retroactively mutating existing specialized packages. Existing packages retain their current metadata until their maintainers supply the evidence required for an explicit maturity decision.

## Maturity model

| Status | Meaning | Permitted wording | Required evidence |
|---|---|---|---|
| `candidate` | Concept, design, or unverified procedure | “designed to,” “requires,” “proposed” | Scope, owner, known prerequisites, test plan |
| `active` | Repeatable in the declared environment | “can,” “produces,” “validated by” | Available dependencies, reproducible local validation, evidence record |
| `conditional` | Usable only after named preflight checks pass | “available when,” “requires verified” | Active preflight and a clear fallback route |
| `deprecated` | Kept for compatibility only | “deprecated; do not select” | Replacement or retirement decision |

## Readiness gate

Before selecting an advanced capability, record the following:

1. **Claim boundary.** What can the capability actually do now, in what environment, and what does it explicitly not prove?
2. **Dependency inventory.** Identify executable tools, scripts, models, data, licenses, account access, hardware, external services, and human approval requirements.
3. **Resource preflight.** Verify that every required item exists, is accessible, matches the expected version, and is allowed for the mission.
4. **Validation evidence.** Run or inspect the stated local acceptance check and preserve its exact output or artifact reference.
5. **Fallback.** If a prerequisite is missing or validation fails, mark the route blocked or candidate, record the owner, and return a safe next action.

## Claim discipline

Do not use absolute claims such as “court-certified,” “tamper-proof,” “zero data loss,” “air-gapped,” “100%,” or “autonomous” unless the exact requirement, environment, evidence, and limitation are documented. Prefer scoped claims: “hash manifest generated for the supplied files,” “test command passed at revision X,” or “designed to preserve originals when the declared procedure is followed.”

Never infer an operational dependency from a filename in a Skill. If a procedure refers to a script, executable, service, dataset, model, or credential, treat it as unavailable until the preflight records a verified source and version.

## Use in the hierarchy

`capability-admission`, `resource-preflight`, and `claim-calibration` are atomic Skills. Their required composition is `capability-readiness`. A Mega Skill may select this Combo before an advanced route whose dependencies, evidence, or claim boundaries are not already verified.
