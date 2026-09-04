# DR-2026-09-03 — Deep Casebuilding Cluster Activation

## Status

Accepted. Implemented on branch `casebuild/deep-casebuilding-activation-20260903`.

## Context

The casebuilding capability chain was present in the registry but inert:

- `audio-forensic-core`: six explicit implementation stubs (ENF, WhisperX, diarization, SHA-256 audit, Bates, transcript formatting).
- `forensic-evidence-chain-core`: six explicit implementation stubs (anomaly scan, timestamps, digests, Bates, PII, manifest).
- `epistemic-gate`: real implementations without behavioral verification, plus two latent defects (`sha256_verifier.py` used `Tuple` without importing it; `tier_evaluator.py` crashed on missing targets instead of failing closed at L0).
- Combos `court-evidence-compiler`, `voice-evidence-authenticator`, `forensic-docket-intelligence`, `epistemic-verification-chain`: `composition_candidate`, blocked by the three skills above.
- Mega `apex-forensic-litigation-sentinel`: `mission_candidate`, blocked by `forensic-docket-intelligence`.
- Mega `apex-legal-forensic-powerhouse`: active, but routed to generic operating loops (`guarded-automation-loop`, `signal-to-decision-loop`) rather than the legal-forensic chain its name and mission declare.
- `pipelines/`: no casebuilding pipeline.

## Decision

1. Replace all twelve stubs with deterministic, test-covered implementations. Heavy DSP paths (WhisperX alignment, pyannote diarization, compressed-audio ENF extraction) fail closed with structured capability reports; no output is fabricated. Integrity, formatting, and verification paths are fully implemented in stdlib Python.
2. Repair the two `epistemic-gate` defects (`Tuple` import; missing-target L0 handling).
3. Give all three skills assertion-dense behavioral suites (`unittest.TestCase`, pytest-collectable) covering determinism, tamper detection, contiguity, inversion and splice detection, custody chaining, format compliance, and fail-closed gates.
4. Add `pipelines/deep-casebuilding.json` (18 stages) and the `missions/deep-casebuilding/` scaffold: intake validation, hashing, anomaly scan, Bates planning and verification, timeline verification, PII scan, hash-chained manifest emission and re-verification, audio custody, transcript compilation, alignment and diarization verification, the three skill test suites as pipeline stages, and dossier compilation.
5. Extend the 2026-08-31 state-law / journal-source correction to `forensic-docket-intelligence` (1.1.0) and `voice-evidence-authenticator` (0.2.0) so the whole casebuilding cluster is jurisdiction-neutral and original-media-preserving.
6. Rewire `apex-legal-forensic-powerhouse` to required `long-horizon-core` + `forensic-docket-intelligence` + `court-evidence-compiler`, conditional `capability-readiness` + `voice-evidence-authenticator` + `epistemic-verification-chain` + `evidence-to-evolution-loop` (0.2.0); MEGA.md updated in place; the registry edit executes through the activation driver.
7. Registry maturity promotion is performed by the repository's own readiness assay through `scripts/casebuilding_activation.py`: preflight, behavioral proof, fresh `inspect_skill` verdicts, then assay pass-2 `--apply` with a full-clone guard, version sync, and a hash-bound receipt under `evidence/casebuilding-activation/`. No maturity flag is hand-edited; `apex-forensic-litigation-sentinel` promotes when its required combos report ready.

## Evidence

- Sandbox behavioral runs: three suites green (8 + 10 + 7 tests) on Python 3.13.
- Pipeline: 18/18 stages exit 0 on the empty scaffold; dossier compiles.
- Dry-run receipt: `activation_ready=true` with fresh `behavior_verified` verdicts for the three target skills and `composition_ready` verdicts for the four target combos; `apex-forensic-litigation-sentinel` reports `mission_contract_ready` under mixed evidence (fresh targets + recorded dependency readiness).
- Receipts: `evidence/casebuilding-activation/`.

## Safety

- Firewall postures untouched (`read_only`, human control required).
- Original-media invariants are encoded in code: Bates plans are derivative-only; PII redaction writes copies; custody and manifest chains are read-only over evidence.
- Capability gates fail closed (exit 2, `fabricated_results=false`) when WhisperX / pyannote / ffmpeg are absent.

## Rollback

Revert the activation branch commit. Registry promotions reverse by re-running the readiness assay pass 2, because maturity follows evidence.
