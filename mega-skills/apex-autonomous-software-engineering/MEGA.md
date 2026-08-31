# APEX Autonomous Software Engineering Mega Skill

## Mission

Orchestrate autonomous, evidence-driven software engineering from requirement framing through architecture, implementation, test synthesis, security triage, performance profiling, polyglot verification, and release delivery. This Mega Skill unifies specialized engineering skills and compounding combos into an end-to-end, reproducible mission system.

## Compounding structure

| Route Type | Member Combo Skill | What the Mega Layer Adds |
|---|---|---|
| **Mandatory** | `long-horizon-core` | Mission framing, roadmap sequencing, evidence registry, active context compactor, work packets, and safe recovery. |
| **Mandatory** | `architectural-refactoring-engine` | Dependency graph analysis, forbidden boundary detection, and syntax-aware AST transformations. |
| **Mandatory** | `closed-loop-code-repair` | Closed-loop traceback parsing, automated AST defect localization, and 100% green test assertions. |
| **Mandatory** | `guarded-automation-loop` | Safe execution isolation, bounded batches, rollback points, and failure recovery. |
| **Conditional** | `capability-readiness` | Preflight resource vetting, tool admission, and claim calibration before engaging unverified dependencies. |
| **Conditional** | `polyglot-systems-verification` | Formal proofs, Lean 4 / Cap'n Proto / Swift Metal integration via Tower of Babel (51 production floors). |
| **Conditional** | `secure-service-deployment` | Security scanning, credential isolation, container hardening, and guarded deployment gates. |

## End-to-end execution protocol

1. **Frame the mission (`long-horizon-core`)**: Convert requirements into bounded outcome, non-goals, acceptance criteria, risk classification, and approval boundaries. Generate `MISSION.md`.
2. **Inspect reality**: Walk repository tree, read build manifests, CI workflows, dependencies, and active git state. Never assume behavior from filenames.
3. **Map architecture (`architectural-refactoring-engine`)**: Extract typed dependency graph via `automated-architecture-analysis`, detect layering violations, cycles, and blast radius.
4. **Plan smallest slice**: Decompose roadmap into discrete, testable `work-packet` specifications. Generate `ROADMAP.md`.
5. **Implement syntax-aware edits**: Apply bounded, surgical AST modifications via `automated-code-refactoring`. Enforce Google Senior Staff engineering invariants.
6. **Synthesize automated tests (`closed-loop-code-repair`)**: Synthesize regression, boundary, and property tests via `automated-test-generation`. Enforce fail-closed coverage thresholds.
7. **Triage security & secrets (`secure-service-deployment`)**: Execute static analysis, dependency scanning, and secret detection via `automated-security-scanning`. Eliminate vulnerabilities.
8. **Profile performance**: Establish fair baselines, profile bottlenecks, and benchmark latency distributions via `automated-performance-profiling`.
9. **Integrate specialized outputs**: Reconcile cross-combo telemetry and resolve conflicting assumptions in `CONTEXT.md` and `EVIDENCE.md`.
10. **Route Tower of Babel (`polyglot-systems-verification`)**: If polyglot interfaces, MLIR/Metal kernels, or formal truth proofs are involved, execute formal Tower verification gates.
11. **Enforce quality gate**: Verify all acceptance invariants, compiler passes, and green tests via `quality-gate`.
12. **Review delivery**: Maintainer-level AST diff review for naming, clarity, error handling, backward compatibility, and zero credential leakage.
13. **Mutation boundary check**: Enforce APEX Cognitive Firewall: halt at the mutation boundary for explicit authorization before publishing, deploying, or deleting.
14. **Emit engineering receipt**: Generate cryptographic `ENGINEERING_RECEIPT.md` documenting decisions, hashes, tests, and rollback points.
15. **Observe & compound**: Record telemetry, update Hebbian synapses, and compile the final deliverable into `AUTONOMOUS_ENGINEERING_MISSION_RESULT.md`.

## Durable state

Maintains six immutable state files across execution steps and restarts:
- `MISSION.md` — Scoped mission boundary, acceptance criteria, and non-goals.
- `ROADMAP.md` — Dependency-aware ordered work packet execution graph.
- `EVIDENCE.md` — Cryptographic SHA-256 test logs, benchmark data, and scan receipts.
- `CONTEXT.md` — Lean active context capsule preserving critical state.
- `HANDOFF.md` — Bounded recovery and safe resumption state.
- `ENGINEERING_RECEIPT.md` — Formal delivery receipt with verification evidence.

## APEX Cognitive Firewall & Operational Invariants

- **Invariant 1 (Read-Only Default)**: Read, inspect, and analyze before any state mutation. External mutations require explicit user authority.
- **Invariant 2 (Bounded Batching)**: Single conceptual change per slice; zero infinite retry loops or runaway subprocesses.
- **Invariant 3 (Fail-Closed Gate)**: Test failures, security findings, or missing coverage fail the release gate immediately.
- **Invariant 4 (Non-Destructive Rollback)**: Every mutation must have a verified rollback mechanism.
