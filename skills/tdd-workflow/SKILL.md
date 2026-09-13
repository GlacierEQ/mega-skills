---
name: tdd-workflow
description: "Test-Driven Development workflow principles. RED-GREEN-REFACTOR cycle."
---

# TDD Workflow

> Write contract tests first, implementation second.

---

## 1. The TDD Cycle

```
🔴 RED → Write failing contract test
    ↓
🟢 GREEN → Implement the complete justified behavior
    ↓
🔵 REFACTOR → Strengthen code quality and structure
    ↓
   Repeat...
```

---

## 2. The Three Laws of TDD

1. Write production code only to make a failing contract test pass
2. Write enough tests to prove required behavior, edge cases, and failure handling
3. Write the complete implementation required by the contract; do not add unrelated speculative features

---

## 3. RED Phase Principles

### What to Write

| Focus | Example |
|-------|---------|
| Behavior | "should add two numbers" |
| Edge cases | "should handle empty input" |
| Error states | "should throw for invalid data" |
| Integration | "should expose the behavior through the real entry point" |

### RED Phase Rules

- Test must fail first
- Test name describes expected behavior
- One coherent behavior per test; split only independent contracts
- Include required edge/error paths

---

## 4. GREEN Phase Principles

### Contract-Complete Code

| Principle | Meaning |
|-----------|---------|
| **YAGNI** | Avoid unrelated speculative surface, not required capability |
| **Strongest justified path** | Implement the complete acceptance contract |
| **No premature optimization** | Verify behavior first, then optimize against real requirements and measurements |

### GREEN Phase Rules

- Implement the complete requested behavior
- Do not add unrelated speculative code
- Do not omit required resilience, edge cases, integration, or observability merely to shrink the diff

---

## 5. REFACTOR Phase Principles

### What to Improve

| Area | Action |
|------|--------|
| Duplication | Extract common code without losing unique behavior |
| Naming | Make intent clear |
| Structure | Improve organization and composability |
| Complexity | Simplify only when behavior and capability are preserved |
| Resilience | Strengthen failure handling and recovery where required |

### REFACTOR Rules

- All tests must stay green
- Use coherent increments sized to the change, not arbitrary tiny slices
- Commit after each meaningful refactor

---

## 6. AAA Pattern

Every test follows:

| Step | Purpose |
|------|---------|
| **Arrange** | Set up test data |
| **Act** | Execute code under test |
| **Assert** | Verify expected outcome |

---

## 7. When to Use TDD

| Scenario | TDD Value |
|----------|-----------|
| New feature | High |
| Bug fix | High (write test first) |
| Complex logic | High |
| Exploratory | High after the spike is converted into a contract |
| UI layout | High for behavior and accessibility contracts |

---

## 8. Test Prioritization

| Priority | Test Type |
|----------|-----------|
| 1 | Core behavior |
| 2 | Error cases |
| 3 | Edge cases |
| 4 | Performance and resilience |
| 5 | Integration and observability where material |

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Skip the RED phase | Watch test fail first |
| Write tests after | Write tests before |
| Add unrelated speculative surface | Implement the complete requested contract |
| Multiple unrelated behaviors in one test | One coherent behavior per test |
| Test implementation | Test behavior |
| Omit required behavior to reduce the diff | Preserve the required capability and prove it |

---

## 10. AI-Augmented TDD

### Multi-Agent Pattern

| Agent | Role |
|-------|------|
| Agent A | Write contract tests (RED) |
| Agent B | Implement the complete contract (GREEN) |
| Agent C | Strengthen, refactor, and adversarially verify (REFACTOR) |

---

> **Remember:** The test is the specification. If you can't write a test, you don't understand the requirement.
