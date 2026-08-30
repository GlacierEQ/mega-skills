---
id: architectural-refactoring-engine
display_name: Architectural Refactoring Engine
schema: ../../schemas/combo-skill.schema.json
version: 1.0.0
status: active
---

# Architectural Refactoring Engine

## Purpose and selection

Elevating legacy modules to production standards with zero regressions.
Do **not** use when minor single-line typo or lint formatting changes.

## Incremental value

Closed-loop architectural transformation: connects high-level ADR design with clean implementation, automated AST patching, and peer-grade code review.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `architecture` | Skill | Yes | Analyze system design, evaluate trade-offs, and generate Architecture Decision Records. | Target codebase directory, Refactoring requirements | ARCHITECTURE_DECISION_RECORD.md, Target interface contracts | ADR clearly defines trade-offs, interface boundaries, and invariant requirements. |
| 2 | `clean-code` | Skill | Yes | Refactor implementation to pragmatic standards with zero bloat and explicit typing. | ARCHITECTURE_DECISION_RECORD.md, Existing source files | Refactored source tree, Strict typing annotations | All magic numbers removed, type coverage 100%, cyclomatic complexity bounded. |
| 3 | `ast-repair-core` | Skill | Yes | Parse AST tracebacks, locate structural defects, and apply surgical patches. | Refactored source tree, Compiler/test execution logs | Synthesized AST patches, Green compiler receipts | Zero syntax errors, zero unresolved imports, 100% clean AST parse. |
| 4 | `code-review-checklist` | Skill | Yes | Execute comprehensive audit for security, maintainability, and concurrency safety. | Refactored source tree, Compiler receipts | CODE_REVIEW_AUDIT.md, Remediation directives | Security, performance, and maintainability dimensions meet staff engineer standards. |
| 5 | `quality-gate` | Skill | Yes | Verify test assertion pass rates, typecheck completion, and invariant adherence. | CODE_REVIEW_AUDIT.md, Test suite execution receipts | ARCHITECTURAL_REFACTORING_RECORD.md, Release approval | 100% test pass rate with zero behavioral regressions. |

## Ordered execution

1. **Step 1 — `architecture`**: Consumes Target codebase directory, Refactoring requirements, produces ARCHITECTURE_DECISION_RECORD.md, Target interface contracts, and satisfies: ADR clearly defines trade-offs, interface boundaries, and invariant requirements.
2. **Step 2 — `clean-code`**: Consumes ARCHITECTURE_DECISION_RECORD.md, Existing source files, produces Refactored source tree, Strict typing annotations, and satisfies: All magic numbers removed, type coverage 100%, cyclomatic complexity bounded.
3. **Step 3 — `ast-repair-core`**: Consumes Refactored source tree, Compiler/test execution logs, produces Synthesized AST patches, Green compiler receipts, and satisfies: Zero syntax errors, zero unresolved imports, 100% clean AST parse.
4. **Step 4 — `code-review-checklist`**: Consumes Refactored source tree, Compiler receipts, produces CODE_REVIEW_AUDIT.md, Remediation directives, and satisfies: Security, performance, and maintainability dimensions meet staff engineer standards.
5. **Step 5 — `quality-gate`**: Consumes CODE_REVIEW_AUDIT.md, Test suite execution receipts, produces ARCHITECTURAL_REFACTORING_RECORD.md, Release approval, and satisfies: 100% test pass rate with zero behavioral regressions.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `architecture` | `clean-code` | ARCHITECTURE_DECISION_RECORD.md | Refactored source tree | system-architect |
| `clean-code` | `ast-repair-core` | Refactored source tree | Synthesized AST patches | lead-coder |
| `ast-repair-core` | `code-review-checklist` | Synthesized AST patches | CODE_REVIEW_AUDIT.md | ast-engineer |
| `code-review-checklist` | `quality-gate` | CODE_REVIEW_AUDIT.md | ARCHITECTURAL_REFACTORING_RECORD.md | auditor |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Architecture Decision Record documenting trade-offs.
- Static AST verification logs with zero parse errors.
- Comprehensive code review audit report.

Risk boundaries:
- Zero breaking changes to external public API contracts.
- Zero untested code paths committed to main branch.

## Quality gates

- Pytest / unit test pass rate = 100%.
- Strict typing validation with zero type errors.

## Compound output

**Artifact:** `ARCHITECTURAL_REFACTORING_RECORD.md`

**Ready for Mega Skill integration when:**

1. Refactored code achieves 100% test pass rate.
2. Code review checklist flags zero high or critical risks.
