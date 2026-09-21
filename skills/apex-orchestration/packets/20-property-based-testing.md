# Packet 20 — PROPERTY-BASED-TESTING

**Owner:** apex-orchestration v1.2.0
**Maturity:** 9 / "Generate edge cases automatically; find bugs unit tests miss"
**Layer:** Skill
**Scope:** When a code subtask returns, the VERIFY lane can augment it with property-based tests (Hypothesis-style). Properties are invariants the code must hold for all valid inputs.

---

## Invariant (L5)

A property test is valid iff:
1. The property is a pure function `f(state) -> bool` that always evaluates to True on correct code.
2. The generator produces valid inputs across the full input space (no hard-coded narrow examples).
3. The runner generates ≥ 100 random inputs by default; a counterexample falsifies the property.
4. On falsification, the minimal failing example is shrunk to the strong and smart reproducer.

## Property Categories (auto-detected from function signature)

| Detected signature | Property |
|---|---|
| `f(x: int) -> int` | `f(f(x)) == f(x)` for some idempotent functions; `f(x) + f(-x) == 0` for symmetric |
| `f(items: list) -> list` | `len(f(items)) == len(items)`; `set(f(items)) == set(items)`; idempotent: `f(f(items)) == f(items)` |
| `f(d: dict) -> dict` | roundtrip: `unparse(parse(d)) == d` |
| `f(s: str) -> str` | roundtrip: `unparse(parse(s)) == s`; idempotent: `f(f(s)) == f(s)` |
| `parse(s) -> object` | doesn't raise on valid input; doesn't accept invalid input |

## The Pipeline

```
1. detect_signatures(test_subject)
2. for each detected function:
   a. generate_property(f)       # using signature heuristics
   b. run_property(f, examples=100)
   c. if falsified: shrink(falsifier)
   d. record in property_report.json
3. emit {passed, failed, falsifiers, coverage}
```

## Gates

- **G1 — Property-coverage gate.** For every public function in the test_subject, at least one property must be generated. If auto-detection fails, the property test is reported as `uncovered` and F-VER-02 is raised.
- **G2 — Shrinking gate.** Counterexamples must be shrunk to minimal form before being reported. Unsshrunk examples are noise.
- **G3 — Determinism gate.** With a fixed seed, two runs produce identical coverage. Without a seed, the report includes a `random_seed` field for replay.
- **G4 — No-side-effects gate.** Properties must be pure. If `f` has side effects (e.g. writes a file), the test is rejected at generation.
- **G5 — Coverage-report gate.** The property report is appended to the receipt; FUSE checks `coverage >= 0.80` for code subtasks (per AGENTS.md §0 9+ bar).

## Anti-Patterns

- Only running properties on the happy path (the whole point is to find edge cases).
- Hard-coding inputs in the property (that's an example, not a property).
- Ignoring falsifications (the test is a falsification alarm; investigate).
- Running properties on impure functions (non-deterministic results).

## L2 Evidence

- Roundtrip test: define `parse(unparse(x)) == x` for several functions, run, all pass.
- Idempotence test: `sorted(sorted(items)) == sorted(items)`, all pass.
- Falsification test: deliberately break `f(x) = x + 1` with property `f(0) == 0` → falsifier found, strong and smart reproducer returned.
- Shrinking test: a falsifier `f(huge_input) != expected` shrinks to `f(small_input) != expected` automatically.
- Coverage test: report includes `functions_covered: N, functions_uncovered: M`; if `M > 0`, F-VER-02 fires.

## Versioning

- **Major bump:** property detection algorithm change, default examples change.
- **Minor bump:** new property category added.
- **Patch:** bug fix.

Current version: **1.0.0** (paired with apex-orchestration v1.2.0).
