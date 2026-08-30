---
name: polyglot-systems-verification
description: 'Combo Skill: Polyglot Systems Verification. Reusable capability chain.'
---

# Polyglot Systems Verification

## Purpose and selection

Use this Combo Skill when high-performance algorithms, zero-copy IPC protocols, or formal truth invariants must be translated, compiled, and verified across the 51 floors of The Tower of Babel. Do **not** use it for simple single-language script execution.

## Incremental value

This Combo Skill establishes an end-to-end multi-language verification bridge, proving behavioral equivalence and zero-copy performance across Rust, C++, eBPF, CUDA, and Lean 4 without manual porting defects.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set target language floors and invariant criteria | System mandate | `MISSION.md` | Language floors and constraints are explicit |
| 2 | `polyglot-rosetta-core` | Skill | Yes | Translate, compile, benchmark, and verify | `MISSION.md` and source AST | `polyglot-verification-receipt.json` | Cross-language compilation and benchmarks pass |
| 3 | `quality-gate` | Skill | Yes | Verify formal proofs and latency budgets | Receipts and benchmarks | Gate record | Zero memory leaks and formal proofs verified |

## Ordered execution

1. **Language boundary — `mission-contract`** consumes system mandates and source code, produces `MISSION.md`, and passes when target language floors and performance budgets are defined.
2. **Compilation and translation — `polyglot-rosetta-core`** consumes `MISSION.md`, produces `polyglot-verification-receipt.json`, and passes when binaries compile and formal proofs verify invariants.
3. **Systems gate — `quality-gate`** consumes receipts and benchmarks, produces a gate record, and passes when zero memory leaks and formal invariants are validated.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `polyglot-rosetta-core` | Source AST, target floor, invariant spec | Compiled binaries, benchmark logs, Lean 4 proofs | systems architect | Target floors and invariants are explicit |
| `polyglot-rosetta-core` | `quality-gate` | Verification receipts, latency metrics | Verified gate record | verification owner | 100% assertions green and proofs verified |

## Evidence, risks, and state

The Combo must record all compiler flags, benchmark TTFT/latency numbers, binary hashes, and formal proof receipts in its evidence register. It must not generate non-functional stubs. Update active state after each floor transition.

## Quality gates

The Combo is complete only when all target language binaries compile without warnings, performance meets latency thresholds, formal proofs pass Lean 4 checks, and `polyglot-systems-record.md` is emitted.

## Compound output

**Artifact:** `polyglot-systems-record.md`

**Ready for Mega Skill integration when:**

1. Cross-language binary compilation passes with zero errors.
2. Formal mathematical invariant proofs verify in Lean 4.
3. Sub-microsecond IPC latency benchmarks are recorded.
