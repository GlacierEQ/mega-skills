---
name: characterization-tests-first
description: "Before upgrading untested legacy code, pin its current behavior with characterization tests (Michael Feathers, Working Effectively with Legacy Code) so the upgrade is verified against observed behavior, not hope."
---

# Characterization Tests First

Make legacy upgrades verifiable: write tests that document what the code actually does today — including its quirks — before any change, so the upgrade's correctness is judged against pinned behavior.

## Workflow

1. Bound the area about to change; identify its entry points and real input sources.
2. Generate characterization cases from real inputs; record actual outputs as expectations.
3. Write the quirk register alongside the suite; flag each surprising pinned behavior.
4. Run the suite against the untouched code: it must pass 100% before any upgrade step begins.
5. Hand the suite to the upgrade as its verification baseline; behavior changes during the upgrade require explicit quirk-register dispositions.
6. After the upgrade, the suite (minus deliberately dispositioned quirks) is the parity evidence for spiral-promotion-gate.

## The method

**Provenance:** published method — Michael Feathers, *Working Effectively with Legacy Code*. Registered as knowledge with attribution; no code is lifted.

A characterization test does not assert what the code *should* do; it asserts what the code *does*. The method:

1. **Feed real inputs.** Run the code under characterization with inputs drawn from real usage, not invented cases.
2. **Record actual outputs.** Capture what the system produces — including outputs that look wrong. Write the test to expect exactly that.
3. **Register the quirks.** Every pinned behavior that surprises gets a line in the quirk register: pinned because observed, decision pending. The register is what stops a future upgrader from "fixing" load-bearing behavior mid-migration.
4. **Change under the net.** With behavior pinned, the upgrade proceeds; any test that moves is a named, reviewable behavior change — deliberate or a regression, but never silent.

## Safety gates

- Never write characterization expectations from documentation or intention — only from observed behavior.
- Never silently update a characterization test during an upgrade; a moved pin is a decision and goes in the register.
- A characterization suite that does not pass on untouched code characterizes nothing — fix the harness first.

## Output contract

- Characterization test suite pinning current behavior
- Quirk register: pinned behaviors that look wrong but are load-bearing

## Related skills

- automated-test-generation — generates the test volume this method directs
- strangler-fig-migration — consumes these tests as per-slice parity evidence
- branch-by-abstraction — uses them as the contract for both implementations
- spiral-promotion-gate — judges parity evidence this method produces

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/characterization-tests-first/tests -v
git diff --check
```
