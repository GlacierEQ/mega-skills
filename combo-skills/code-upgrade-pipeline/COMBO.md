---
id: code-upgrade-pipeline
display_name: Code Upgrade Pipeline
schema: ../../schemas/combo-skill.schema.json
version: 1.0.0
status: active
---

# Code Upgrade Pipeline

## Purpose and selection

Upgrading, modernizing, or migrating code across one or more GlacierEQ repositories under evidence gates. Retiring deprecated APIs, flags, or frameworks estate-wide with proof of completion.
Do **not** use when single-file typo, lint, or one-line fixes. or net-new feature development with no upgrade or migration component.

## Incremental value

One governed pipeline for code upgrades — assess, decide, transform, verify, promote — where every stage is owned by a registered skill and every transition is receipted, so an upgrade is provable end-to-end instead of asserted.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `automated-architecture-analysis` | Skill | Yes | Assess: build the typed dependency graph; find cycles, forbidden edges, and the safe decoupling order. | Target repository set, Upgrade goal | Dependency graph and decoupling plan, Risk register | Graph covers every in-scope repository; cycles and forbidden edges are named with a decoupling order. |
| 2 | `characterization-tests-first` | Skill | Yes | Assess: pin the current behavior of untested legacy code before it changes. | Decoupling plan, Legacy code areas | Characterization test suite, Quirk register | Suite passes 100% on untouched code; surprising behaviors are registered, not assumed. |
| 3 | `dependency-update-operator` | Skill | Yes | Decide (feed): produce governed dependency-update candidates via the Dependabot baseline and Renovate patterns. | Repository inventory, Update policy | Update candidate ledger, dependabot.yml / renovate configuration | Every repository has an update posture; candidates are grouped, scheduled, and classified patch/minor/major. |
| 4 | `spiral-promotion-gate` | Skill | Yes | Decide: judge each candidate on parity, rollback readiness, and measured gain; issue or withhold the promotion grant. | Update candidate ledger, Before/after quality states | Promotion decision and chained receipt, Promotion grant (on PROMOTE) | No candidate advances without parity, rollback, and measured-gain evidence. |
| 5 | `automated-code-refactoring` | Skill | Yes | Transform: run bounded, reversible transformation batches under a changed-file budget. | Decoupling plan, Approved transformation scope | Bounded transformation batches, Refactor receipts | Each batch is one conceptual change, within budget, and independently reversible. |
| 6 | `openrewrite-recipes` | Skill | No | Transform (JVM lane): execute API migrations and deprecation removal as versioned OpenRewrite recipes. | API migration specification, Recipe list | Recipe dry-run diff, Applied migration diff | Dry-run diff reviewed before apply; one recipe per batch. |
| 7 | `ast-grep-structural-rewrite` | Skill | No | Transform (polyglot lane): execute structural rewrites by AST pattern with audited match sets. | Structural pattern set, Target trees | Audited match list, Rewrite diff | Match set audited for false positives; post-run search returns zero live matches. |
| 8 | `deprecation-removal` | Skill | No | Transform: retire deprecated surfaces after consumers migrate; prove zero remaining references. | Deprecated surface inventory, Retirement decision record | Consumer dispositions, Deletion diff with zero-reference proof | No surface deleted with live consumers; absence proven by search output. |
| 9 | `test-drift-archaeology-repair` | Skill | Yes | Verify: return a drifted suite to green by archaeology, without weakening a single test. | Full suite failure enumeration, Git history | Green suite, Drift root-cause record | Full suite green with zero tests weakened, skipped, or deleted. |
| 10 | `verification-before-completion` | Skill | Yes | Verify: block any completion claim that lacks command output. | All stage receipts, Suite and build output | Verification verdict | Every completion claim in the record cites command output. |
| 11 | `release` | Skill | Yes | Promote: run release gates, bump the version, commit and push to main. | Promotion grant, Verification verdict | Version bump and artifacts, Commit and push to main | Release gates pass; the upgrade lands on main with receipts attached. |

## Ordered execution

1. **Step 1 — `automated-architecture-analysis`**: Consumes Target repository set, Upgrade goal, produces Dependency graph and decoupling plan, Risk register, and satisfies: Graph covers every in-scope repository; cycles and forbidden edges are named with a decoupling order.
2. **Step 2 — `characterization-tests-first`**: Consumes Decoupling plan, Legacy code areas, produces Characterization test suite, Quirk register, and satisfies: Suite passes 100% on untouched code; surprising behaviors are registered, not assumed.
3. **Step 3 — `dependency-update-operator`**: Consumes Repository inventory, Update policy, produces Update candidate ledger, dependabot.yml / renovate configuration, and satisfies: Every repository has an update posture; candidates are grouped, scheduled, and classified patch/minor/major.
4. **Step 4 — `spiral-promotion-gate`**: Consumes Update candidate ledger, Before/after quality states, produces Promotion decision and chained receipt, Promotion grant (on PROMOTE), and satisfies: No candidate advances without parity, rollback, and measured-gain evidence.
5. **Step 5 — `automated-code-refactoring`**: Consumes Decoupling plan, Approved transformation scope, produces Bounded transformation batches, Refactor receipts, and satisfies: Each batch is one conceptual change, within budget, and independently reversible.
6. **Step 6 — `openrewrite-recipes`**: Consumes API migration specification, Recipe list, produces Recipe dry-run diff, Applied migration diff, and satisfies: Dry-run diff reviewed before apply; one recipe per batch.
7. **Step 7 — `ast-grep-structural-rewrite`**: Consumes Structural pattern set, Target trees, produces Audited match list, Rewrite diff, and satisfies: Match set audited for false positives; post-run search returns zero live matches.
8. **Step 8 — `deprecation-removal`**: Consumes Deprecated surface inventory, Retirement decision record, produces Consumer dispositions, Deletion diff with zero-reference proof, and satisfies: No surface deleted with live consumers; absence proven by search output.
9. **Step 9 — `test-drift-archaeology-repair`**: Consumes Full suite failure enumeration, Git history, produces Green suite, Drift root-cause record, and satisfies: Full suite green with zero tests weakened, skipped, or deleted.
10. **Step 10 — `verification-before-completion`**: Consumes All stage receipts, Suite and build output, produces Verification verdict, and satisfies: Every completion claim in the record cites command output.
11. **Step 11 — `release`**: Consumes Promotion grant, Verification verdict, produces Version bump and artifacts, Commit and push to main, and satisfies: Release gates pass; the upgrade lands on main with receipts attached.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `automated-architecture-analysis` | `characterization-tests-first` | Dependency graph and decoupling plan | Characterization test suite | assessor |
| `characterization-tests-first` | `dependency-update-operator` | Characterization test suite | Update candidate ledger | test-engineer |
| `dependency-update-operator` | `spiral-promotion-gate` | Update candidate ledger | Promotion decision and chained receipt | dependency-operator |
| `spiral-promotion-gate` | `automated-code-refactoring` | Promotion decision and chained receipt | Bounded transformation batches | promotion-authority |
| `automated-code-refactoring` | `openrewrite-recipes` | Bounded transformation batches | Recipe dry-run diff | lead-coder |
| `openrewrite-recipes` | `ast-grep-structural-rewrite` | Recipe dry-run diff | Audited match list | recipe-engineer |
| `ast-grep-structural-rewrite` | `deprecation-removal` | Audited match list | Consumer dispositions | transform-engineer |
| `deprecation-removal` | `test-drift-archaeology-repair` | Consumer dispositions | Green suite | retirement-engineer |
| `test-drift-archaeology-repair` | `verification-before-completion` | Green suite | Verification verdict | repair-engineer |
| `verification-before-completion` | `release` | Verification verdict | Version bump and artifacts | verifier |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Dependency graph and decoupling plan for the assessed scope.
- Full before/after test-suite outputs for every transformed repository.
- SHA-256-chained promotion receipts for every promoted candidate.
- Zero-reference search output for every retired deprecated surface.

Risk boundaries:
- No transformation batch exceeds its changed-file budget or crosses its approved scope.
- No candidate is promoted without parity and rollback evidence (Spiral Promotion Gate).
- Deprecated surfaces are never deleted while live consumers remain.
- Renovate code is never lifted into the estate (AGPL-3.0); it runs as a tool or service only.

## Quality gates

- Full test suite green in every transformed repository.
- Dry-run diff reviewed before every recipe or codemod application.
- Zero tests weakened, skipped, or deleted to reach green.

## Compound output

**Artifact:** `CODE_UPGRADE_RECORD.md`

**Ready for Mega Skill integration when:**

1. A full upgrade run completes with all stage receipts chained.
2. Zero unresolved REVISE signals remain in the run record.
