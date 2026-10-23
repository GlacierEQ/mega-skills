---
name: re-reconstruction-verification
description: "Rebuilding behavior from reverse-engineering evidence and proving it: typed reconstruction specifications, readiness and coverage ledgers, obligation tracking, and verify_reconstruction — a pass covers exactly the declared claims, verified against the original by test."
---

# RE Reconstruction & Verification

Own the payoff stage: a reconstruction is a claim, and this skill makes it a verified one. REA's verification model is deliberately narrow — `verify_reconstruction` evaluates a finite typed specification — and that narrowness is the point: a pass covers only declared comparable claims, never global equivalence.

## Workflow

1. Derive the specification from the ledger: each comparable claim (input/output behavior at a boundary, a function's results over a test corpus, a protocol exchange) is typed and finite. Behavior the evidence never established does not enter the spec — it enters the unknowns.
2. Track readiness before building: REA's reconstruction-readiness, coverage, and obligation ledgers state what evidence a reconstruction still owes. A reconstruction started against an unready ledger is speculation with a build step.
3. Build with normal coding tools, keeping observed behavior and design choices visibly separate (REA's own finishing rule): where the original was observed, the reconstruction follows the observation; where it was not, the choice is the builder's and is recorded as such.
4. Verify against the original by test: run the reconstruction and the original over the spec's corpus and compare at the level the spec declares — behavior, outputs, and where the evidence supports it, byte/diff level. REA's showcase standard is the bar: a reconstructed function that passes thousands of generated cases against the original binary and reproduces its compiled bytes exactly.
5. Report at claim scope: passed claims, failed claims, unverified claims — three lists, never one blended verdict. Feed failures and newly exposed unknowns back into the ledger (re-evidence-record) as the next investigation round.

## Safety gates

- Lawful reconstruction only: interoperability, preservation, security research, and software the operator owns or is authorized to rebuild. Copying proprietary code/assets or defeating protections is excluded (re-safety-gate) no matter how complete the evidence is.
- A verified pass is never restated as "identical to the original" — the claim-scope statement travels with the result wherever it is cited.

## Output contract

- Reconstruction + typed specification + verification result
- Claim-scope statement (passed / failed / unverified) and updated obligation ledger

## Related skills

- re-evidence-record — the ledger the specification derives from
- re-version-comparison — differential evidence for regression claims
- verification-before-completion — the estate-wide completion-claim gate
- reverse-engineering-pipeline — this skill is its VERIFY terminus

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-reconstruction-verification/tests -v
git diff --check
```
