---
id: web-build-foundation
display_name: Web Build Foundation
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Web Build Foundation

## Purpose and selection

Use this Combo when a web experience needs an evidence-led route from repository reconnaissance through visual direction, coded implementation, capability escalation, and local verification. Do **not** use it as a substitute for specialist product, legal, medical, financial, or domain validation; route those concerns to the applicable specialist capability before accepting the build.

## Incremental value

The selected members each own a distinct method. This Combo adds the ordered handoff from source-of-truth discovery to visual and implementation decisions, then to the smallest justified full-stack escalation and a reproducible verification receipt. No member independently owns that complete web-build route.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `repository-context-onboarding` | external Skill | Yes | Map repository ownership, source of truth, constraints, and related systems without mutating them. | User request and repository target | `REPOSITORY_CONTEXT.md` | Target, revision, relevant files, and unresolved questions are recorded. |
| 2 | `imagegen` | external Skill | Yes | Decide whether visuals require generated assets, deterministic diagrams, or coded UI, then write a visual brief. | `REPOSITORY_CONTEXT.md`, design intent, asset inventory | `VISUAL_DIRECTION.md` and asset route decisions | Every prominent visual has a selected production route and acceptance risk. |
| 3 | `webdev-readme-static` | external Skill | Yes | Implement the browser experience with the project’s template, accessibility, responsive, asset, and interaction rules. | Repository map and visual direction | Working frontend change | Type check/build and route-level browser inspection pass. |
| 4 | `webdev-readme-fullstack` | external Skill | Conditional | Escalate only when authenticated state, database, storage, API proxying, or other real product behavior is required. | Static implementation and verified feature requirement | `FULLSTACK_ESCALATION_RECORD.md` and approved feature plan | Required schema, server, test, and secret boundaries are explicit before escalation. |
| 5 | `mega-skills-test-runner` | skill | Yes | Run the canonical hierarchy validator, regression suite, and diff-hygiene check; preserve exact evidence. | Repository revision and implementation diff | `MEGA_SKILLS_VALIDATION.json` | All required checks return zero unless the route is explicitly blocked with evidence. |

## Ordered execution

1. **Map the terrain — `repository-context-onboarding`** consumes the request and trusted checkout, producing `REPOSITORY_CONTEXT.md` with revision, ownership, source-of-truth files, constraints, and unresolved facts.
2. **Set the visual route — `imagegen`** consumes the context map and design intent, producing `VISUAL_DIRECTION.md`, asset decisions, and a bounded visual brief. It must not replace functional implementation with image-only output.
3. **Build the browser artifact — `webdev-readme-static`** consumes the context and visual route, producing the working frontend with responsive behavior, accessible interaction states, and valid asset references.
4. **Escalate only when observed requirements demand it — `webdev-readme-fullstack`** consumes a verified feature gap and produces a full-stack escalation record; when no such gap exists, record `NOT_REQUIRED` and continue with the static route.
5. **Verify the repository state — `mega-skills-test-runner`** consumes the complete diff and current revision, producing a machine-readable validation receipt with commands, outputs, exit codes, and residual limitations.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `repository-context-onboarding` | `imagegen` | Repository map, brand constraints, asset inventory | Visual route with scenario and acceptance risks | Context owner | No visual work starts against an unknown source of truth. |
| `imagegen` | `webdev-readme-static` | Visual brief, chosen asset route, text/contrast constraints | Implementable visual system and asset references | Design owner | All prominent visuals have a production route and no asset is silently mocked. |
| `webdev-readme-static` | `webdev-readme-fullstack` | Verified feature requirement, current frontend, integration boundary | Escalation record or explicit `NOT_REQUIRED` decision | Product owner | Full-stack work is admitted only when static behavior cannot satisfy the requirement. |
| `webdev-readme-fullstack` | `mega-skills-test-runner` | Migration/API/test plan or `NOT_REQUIRED` record | Verifiable repository change | Implementation owner | Required build, test, and schema evidence is available. |

## Evidence, risks, and state

Record source URLs or repository paths, revision identifiers, design decisions, asset provenance, implementation commands, browser observations, tests, and limitations. The Combo must not expose secrets, mutate an external repository, deploy, create schedules, poll services, or claim live capability that was not observed. A full-stack escalation must remain behind explicit user approval and the project’s feature setup route.

## Quality gates

The Combo is complete only when the source of truth is mapped, the visual route is explicit, the browser artifact is buildable and accessible, full-stack escalation is either justified or explicitly unnecessary, and the validation receipt is reproducible. An unresolved failure remains a blocked handoff rather than an implied success.

## Compound output

**Artifact:** `WEB_BUILD_FOUNDATION_RECORD.md`, containing the repository map, visual decision, implementation route, escalation decision, validation receipt, residual uncertainty, and next compatible action.

**Ready for Mega Skill integration when:**

1. The five member outputs are present or explicitly marked conditionally not required.
2. Every handoff names its inputs, output shape, owner, and close condition.
3. A non-creator can reconstruct why the route was chosen and reproduce its verification.
