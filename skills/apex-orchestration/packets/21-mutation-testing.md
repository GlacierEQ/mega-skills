# Packet 21 — MUTATION-TESTING

**Owner:** apex-orchestration v1.2.0
**Maturity:** 9 / "Verify the test suite actually catches bugs; ≥80% mutation score"
**Layer:** Skill
**Scope:** After a code subtask passes, mutate the source (flip operators, replace constants, change conditionals) and confirm tests still fail. If tests don't fail on the mutation, the test suite is weak.

---

## Invariant (L5)

A mutation test is valid iff:
1. A mutation is a single, small, semantic change to the source code (one operator flipped, one constant changed, one return value swapped).
2. The test suite must FAIL on the mutated source.
3. If the test suite PASSES on the mutated source, the mutation "survived" → the test suite is weak at that point.
4. Mutation score = (killed mutations) / (total mutations). Target: >= 0.80.

## Mutation Operators (closed set)

| Operator | Example |
|---|---|
| `AOR` (arithmetic op replace) | `+` → `-`, `*` → `/` |
| `LOR` (logical op replace) | `&&` → `\|\|`, `!` → (delete) |
| `ROR` (relational op replace) | `<` → `<=`, `==` → `!=` |
| `UOI` (unary op insert) | `if (x)` → `if (!x)` |
| `CRP` (constant replace) | `0` → `1`, `""` → `"mutant"` |
| `RVR` (return value replace) | `return x` → `return None` |
| `SDL` (statement delete) | `x++;` → (delete) |
| `MCF` (method call flip) | `obj.method()` → `obj.other_method()` |

## The Pipeline

```
for each mutation_operator:
    for each applicable_site in source:
        mutated = apply_mutation(source, operator, site)
        if tests_pass(mutated):
            surviving_mutations.append({operator, site})
        else:
            killed_mutations += 1
mutation_score = killed / (killed + surviving)
```

## Gates

- **G1 — Mutation-score gate.** `mutation_score >= 0.80` for the test suite to be considered elite. Below that, F-VER-02 fires with the list of surviving mutations.
- **G2 — Operator-coverage gate.** All 8 operators in the closed set must be applied where applicable. An operator with 0 applications means the source has no relevant code; that's recorded but does not block.
- **G3 — Reproducibility gate.** With a fixed seed, two runs produce identical mutation results.
- **G4 — Idempotency gate.** A second run on an unchanged source must produce the same mutation_score.
- **G5 — Time-budget gate.** Mutation testing is expensive (each mutant = one full test run). Cap at 600 seconds per code subtask; report `untested_mutants: N` if truncated.

## Anti-Patterns

- Reporting mutation score without operator coverage (e.g. only running AOR, missing ROR).
- Skipping equivalent mutations (mutations that produce semantically equivalent code) without flagging them — every skip must be justified.
- Capping time too low (false confidence in a low score).
- Capping time too high (delays the FUSE stage).

## L2 Evidence

- Mutation-score test: run mutation on a known-good code with known weak tests; score < 0.80; F-VER-02 fires.
- Operator-coverage test: all 8 operators in closed set are applied at least once in a 100-line file.
- Reproducibility test: same source, two runs with same seed, identical mutation results.
- Idempotency test: same source, two runs without changes, same score.
- Time-budget test: cap at 600s; if exceeded, `untested_mutants` is reported.

## Versioning

- **Major bump:** mutation operator set change, score threshold change.
- **Minor bump:** new operator added.
- **Patch:** bug fix.

Current version: **1.0.0** (paired with apex-orchestration v1.2.0).
