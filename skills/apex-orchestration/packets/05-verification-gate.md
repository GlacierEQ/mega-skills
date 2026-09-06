# Packet 05 — VERIFICATION-GATE

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "L2 proof, adversarial audit, three-signature rule for code"
**Layer:** Skill
**Scope:** Defines what counts as verified work. The operator rejects anything weaker.

---

## Invariant (L5)

A subtask is **verified** iff:

1. Its receipt passes `Packet 03 — Receipt Format`.
2. It is signed by an appropriate verifier (see ladder below).
3. The verifier's output is itself a receipt with `l2_proof: true`.
4. For code subtasks, three signatures are present: producer, auditor, refiner.

## The Verification Ladder

| Level | Verifier | What it proves | When to use |
|------:|----------|----------------|-------------|
| L0 | file exists | presence only | never accepted as verified |
| L1 | AST parses | structural integrity | discovery phase only |
| L2 | receipt with `l2_proof: true` | behavior or statement is true at this moment | minimum bar for delivery |
| L3 | cross-system check | live DB / RPC / external service agrees | backend / infra work |
| L4 | eBPF / runtime profile | bounded resource use, no leaks | production deploys |
| L5 | 4-phase dialectic consensus | multiple independent verifiers agree | cross-domain / irreversible missions |
| L6 | Hebbian self-evolution | the verification itself improved over time | long-running missions |

## Three-Signature Rule (code subtasks)

Every code subtask must collect three independent signatures before FUSE:

| Order | Role | Lane | What it produces |
|------:|------|------|------------------|
| 1 | Producer | CODE or CODE-FAST | `{files, sha256, tests}` with `l2_proof: true` |
| 2 | Auditor | VERIFY | `{findings, severity_counts, approve|reject}` |
| 3 | Refiner | REVIEW | `{diff, complexity_before, complexity_after}` |

If any signature is missing, FUSE blocks. The reject path returns to DISPATCH, not forward to DELIVER.

## Gates

- **G1 — Never trust without L2.** L0 and L1 are not deliveries.
- **G2 — Adversarial gate.** For adversarial tasks (find bugs, audit, demand proof), the VERIFY lane is primary. The producer cannot self-verify.
- **G3 — Code triple-signature gate.** No code ships without three signatures.
- **G4 — Long-context gate.** Inputs over 500k tokens require L2 from LONG-CTX, not from a sub-sampled slice.

## Anti-Patterns

- "It compiled, so it works" (L2 missing for behavior).
- "The model said it's correct" (no receipt).
- Auditor = same instance as producer (no independence).
- Skipping the refiner on "trivial" code (every code subtask, trivial or not).

## L2 Evidence

- `signatures[]` block in `fused.json` listing producer / auditor / refiner.
- For each signature: `lane`, `model`, `ts`, `receipt_sha256`.
- For VERIFY: `findings` array with severity, file, line, evidence, remediation.

## Versioning

Adding a level (e.g. L7) is a major bump. Tightening a gate is a major bump.

Current version: **1.0.0**
