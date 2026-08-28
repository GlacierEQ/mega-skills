# Capability Readiness: Implementation Details

## What is implemented

`capability-readiness` is an active **Combo Skill** that prevents a Mega Skill from treating a declared advanced capability as mission-ready without evidence. It is represented consistently in four layers of the repository.

| Layer | File | Implementation responsibility |
|---|---|---|
| Atomic methods | `skills/capability-admission/`, `skills/resource-preflight/`, `skills/claim-calibration/` | Admit the route, verify prerequisites, and constrain claims. |
| Composition contract | `combo-skills/capability-readiness/COMBO.md` | Defines the four-stage route and the compound readiness record. |
| Canonical registry | `registry/skills.json`, `registry/combo-skills.json` | Resolves IDs, member kinds, ordered steps, handoffs, gates, and compound output. |
| Mega routing | `registry/mega-skills.json`, `mega-skills/far-away-party/MEGA.md` | Makes readiness a conditional route before advanced capability selection. |
| Enforcement | `scripts/validate_hierarchy.py`, `tests/test_hierarchy.py` | Rejects unresolved or unready contract wiring in CI. |

## Runtime artifact flow

```text
candidate route + mission context
        │
        ▼
CAPABILITY_ADMISSION.md
        │  named prerequisites, fallback, owner
        ▼
RESOURCE_PREFLIGHT.md
        │  observed status, access, version, policy fit
        ▼
CLAIM_BOUNDARIES.md
        │  approved wording, limits, evidence scope
        ▼
Capability readiness gate
        │
        ├── admitted → select the documented advanced route
        ├── conditional → complete named prerequisite/recheck first
        └── blocked → return the safe fallback and owner
```

The compound artifact is `CAPABILITY_READINESS_RECORD.md`. It is the only readiness input a Mega Skill should need; it links to the three detailed artifacts rather than copying raw investigation history.

## Registry contract

The `capability-readiness` entry in `registry/combo-skills.json` uses the versioned Combo schema. Its required members are ordered as `capability-admission`, `resource-preflight`, `claim-calibration`, and `quality-gate`. Every member declares its kind, role, and required status. Every step declares what it consumes, produces, and locally validates. The contract also records explicit handoffs, evidence requirements, risk boundaries, quality gates, state updates, and the incremental value added by the Combo.

The Combo is conditional, not a universal burden. It is selected whenever the requested route relies on unverified tools, scripts, services, access, data, runtime conditions, or strong claims. If a current mission already has valid readiness evidence, the combination is not repeated; its existing record is rechecked only at the declared expiry or review trigger.

## Validator integration

The hierarchy validator enforces readiness wiring in three stages.

| Validator function | Enforcement |
|---|---|
| `validate_skills()` | Confirms each readiness atomic Skill is registered, has a matching `SKILL.md` frontmatter name, and exposes purpose, contracts, validation, and non-goals. |
| `validate_combos()` | Confirms `capability-readiness` has at least two resolved members, contiguous ordered steps, complete handoffs, evidence/risk/gate/state requirements, a compound artifact, and a `COMBO.md` that links the canonical schema. |
| `validate_mega()` | Requires every Mega Skill’s `conditional_combos` to include `capability-readiness`; verifies the ID resolves to a registered Combo and cannot overlap with required Combos. |

The regression suite then asserts that the atomic readiness foundations are in the registry, the Combo has the exact ordered member chain, and every registered Mega route exposes readiness as a conditional route. A missing readiness Combo, an unresolved member ID, a noncontiguous step, an incomplete handoff, or a Mega route without the readiness control causes validation to fail before merge.

## Example selection decision

If an advanced route refers to a named script and a specialized dataset, `capability-admission` first states that both are required. `resource-preflight` verifies whether the script exists, whether the dataset is accessible and permitted, and whether the expected version and environment match. `claim-calibration` changes a broad claim such as “produces certified output” to evidence-matched wording if no qualification or validation record exists. The quality gate then records `admitted`, `conditional`, or `blocked`, together with the exact next action.

This is deliberately not an execution engine. It provides the decision and evidence control needed before another documented route performs authorized work.
