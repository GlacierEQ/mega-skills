---
name: apex-ast-sentinel
description: "AST-level syntactic invariant validator and defect sentinel for zero-regression code generation."
---

# Apex Ast Sentinel

## Use this skill when

Use this skill when you need: AST-level syntactic invariant validator and defect sentinel for zero-regression code generation.

## Decision gate

Proceed only when:
1. The requested operational envelope is clearly bounded and input parameters are verified.
2. Execution adheres to baseline Epistemic Tier L2 (Behavioral Proof & Unit Assertions).
3. Safety invariants and cognitive firewall rules are satisfied.

## Creation workflow

1. **Inspect context**: Verify environmental invariants and prerequisite schemas.
2. **Draft contract**: Confirm parameters against `resources/apex-ast-sentinel_schema.json`.
3. **Execute domain scripts**: Run focused procedures under `scripts/`.
4. **Verify assertions**: Confirm 100% green test assertions and cryptographic receipts.
5. **Emit deliverable**: Emit structured output artifact with SHA-256 hash.

## Epistemic Tier & Verification Proofs

- **Operational Baseline**: $\mathcal{L}_2$ (Unit & Behavioral Proof)
- **Verification Command**: `python3 -m unittest discover -s tests -v` or `pytest tests/ -v`
- **Integrity**: Deterministic execution, zero side-channel leakage, cryptographic provenance.

## APEX Cognitive Firewall & Safety Invariants

- **Invariant 1 (Read-Only Default)**: Read and analyze prior to any state mutation. External mutations require explicit authority.
- **Invariant 2 (Bounded Execution)**: Bounded batching, explicit timeouts, and zero infinite loops.
- **Invariant 3 (Fail-Closed Gate)**: Any schema violation, missing dependency, or test failure halts execution immediately.

## Resources

| Resource | Use |
|---|---|
| `resources/apex-ast-sentinel_config.yaml` | Runtime configuration parameters. |
| `resources/apex-ast-sentinel_schema.json` | Input and output validation schema. |

## Commands

```bash
apex-ast-sentinel this-skill
apex-ast-sentinel run
```
