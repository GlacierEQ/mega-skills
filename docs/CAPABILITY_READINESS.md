# Capability Readiness and Claim Discipline

## Why this control exists

A Mega Skills repository may describe ambitious future capability, but a description is not evidence that the needed software, data, access, compute, permissions, or validation environment exists. A capability may be **claimed active** only when its prerequisites and named local validation are reproducible in the declared environment. Missing proof limits the claim; it does **not** forbid evaluating, repairing, rerouting, or retesting the capability.

This document introduces a reusable readiness route rather than retroactively mutating existing specialized packages. Existing packages retain their history. Historical labels are observations, not permanent execution authority; a current probe or changed environment can justify a new maturity decision without erasing prior evidence.

## Maturity model

| Status | Meaning | Permitted wording | Required evidence |
|---|---|---|---|
| `candidate` | Concept, design, or unverified procedure | “designed to,” “requires,” “proposed” | Scope, owner, known prerequisites, test plan |
| `active` | Repeatable in the declared environment | “can,” “produces,” “validated by” | Available dependencies, reproducible local validation, evidence record |
| `conditional` | Current route needs a named dependency | “available when,” “requires verified” | Exact missing prerequisite, alternate route, recheck trigger |
| `deprecated` | Explicitly retired from default selection after a substantive decision; still eligible for re-evaluation | “retired from default routing; reassess when premises change” | Decision authority, specific reason, replacement/retirement evidence, recheck trigger |

## Readiness evaluation — never an invented mission gate

When establishing the *claimed maturity* of an advanced capability, record the following; do not require this ceremony to attempt otherwise-authorized reversible work:

1. **Claim boundary.** What can the capability actually do now, in what environment, and what does it explicitly not prove?
2. **Dependency inventory.** Identify executable tools, scripts, models, data, licenses, account access, hardware, external services, and human approval requirements.
3. **Resource preflight.** Check resources needed for the selected route. Missing proof is `unknown`, not `nonexistent`; absence or incompatibility limits only the affected route.
4. **Validation evidence.** Run or inspect the stated local acceptance check and preserve its exact output or artifact reference.
5. **Fallback and recovery.** If a prerequisite fails, record its exact environment, reason and time; try alternate feasible routes and identify a recheck condition. Do not label the capability, whole mission, or unrelated tools superseded.

## Claim discipline

Do not use absolute claims such as “court-certified,” “tamper-proof,” “zero data loss,” “air-gapped,” “100%,” or “autonomous” unless the exact requirement, environment, evidence, and limitation are documented. Prefer scoped claims: “hash manifest generated for the supplied files,” “test command passed at revision X,” or “designed to preserve originals when the declared procedure is followed.”

Never infer an operational dependency from a filename in a Skill. A script, service, dataset, model, or credential not yet observed is **unverified in this environment**, not intrinsically unavailable. Discover and validate the named item or an equivalent route before making a capability claim.

## Supersession and reactivation

A single failed attempt must not cause permanent retirement, suppression from discovery, or a global `unavailable` conclusion. `deprecated` requires an explicit, scoped retirement decision grounded in functional evidence (not a timeout, auth failure, connector gap, or missing test). Re-evaluate on new evidence, changed infrastructure, verified success elsewhere, or operator reopening. Retain failure receipts as local diagnostics and verified successes as reusable routes; do not treat mirrored copies as independent corroboration. Protective restrictions for credentials, privacy, consequential external actions, and destructive work remain independently binding where applicable.

## Use in the hierarchy

`capability-admission`, `resource-preflight`, and `claim-calibration` are atomic Skills. Their required composition is `capability-readiness`. A Mega Skill may select this Combo before an advanced route whose dependencies, evidence, or claim boundaries are not already verified.

## Readiness-record reconciliation — 2026-10-23

The bulk collection in commit `1cbe82d` (+525 gathered skills) wrote `registry/skill-readiness.json` records directly, assigning every collected skill `instruction_ready` without running `scripts/readiness_assay.py` on it. A later assay run disagreed on 211 of the 525. Reconciliation, per class:

- **137 skills** ship real implementation code with no tests. The stored `instruction_ready` overstated them; corrected to `implementation_unverified` (an instruction-only state cannot certify unverified code).
- **26 skills** are placeholder or thin instruction cards (translation-in-progress stubs pointing at an external path, a blank template, sub-180-character bodies). Corrected to `contract_incomplete`.
- **47 skills** are substantive instruction documents in Spanish or Japanese (or English in vocabulary the assay's keyword list missed). The stored state was right; the assay was wrong. `substantive_instruction` in `scripts/readiness_assay.py` (reconciliation-version 5) now tests multilingual procedural vocabulary and enumerated/sectioned structure instead of an English-only keyword list.
- **1 skill** (`taste-application`) was understated; it carries implementation plus behavioral tests and was corrected up to `behavior_verified`.
- The stored report also omitted one live Mega Skill record (`apex-repository-continuity-steward`); restored from the assay.

Net effect: `ready_total` 1371 → 1209, `not_ready_total` 0 → 163, and a fresh assay agrees with the stored records on state and readiness for every entry. Lesson: a bulk registration must run the assay it feeds; a readiness state written by the collecting process itself is a claim, not evidence.
