---
name: epistemic-gate
description: "6-Tier Epistemic Ladder (L0 to L6) for classifying verification strength without manufacturing execution authority."
---

# Epistemic Gate

## Purpose

Apply the Ascended 6-Tier Epistemic Ladder ($\mathcal{L}_0 \to \mathcal{L}_6$) as an **epistemic promotion model**. It controls what may truthfully be claimed about evidence, behavior, readiness, and completion. It does **not** create Operator authorization, turn missing proof into a global stop condition, or require stronger proof than the dependent claim/action actually needs.

Operator/source authority and epistemic strength are separate dimensions. A proposed action may proceed when it is already authorized by the controlling Operator/source and its dependent safety/provider constraints are satisfied; missing or incomplete non-contradictory proof lowers claim strength and creates bounded verification/enrichment debt rather than silently acquiring permission power.

## Procedure

1. Parse the incoming claim, code artifact, or system action and identify the exact proposition whose strength is being evaluated.
2. Evaluate available evidence against the 6-Tier Epistemic Spectrum:
   - **$\mathcal{L}_0$ (Presence):** File or route exists on disk. No behavior assumed.
   - **$\mathcal{L}_1$ (Structure):** Static AST, function signatures, schema verified.
   - **$\mathcal{L}_2$ (Behavior):** Unit tests pass, SHA-256 verified, compilers green.
   - **$\mathcal{L}_3$ (Colossal Backend):** Live DB integration, RPC mesh, multi-cloud storage sync verified.
   - **$\mathcal{L}_4$ (Telemetry & Self-Healing):** Runtime latency, profiling, zero memory leaks, automated repair confirmed.
   - **$\mathcal{L}_5$ (Swarm Enterprise):** 4-phase dialectic multi-agent consensus reached.
   - **$\mathcal{L}_6$ (Sovereign Autonomy):** Upstream tracking, Hebbian synaptic reinforcement, zero drift.
3. Assign the strongest tier actually supported. Never promote a claim above its evidence.
4. For a dependent claim or transition that needs stronger evidence, record the exact verification/enrichment debt and continue unaffected authorized work. Do not translate `UNKNOWN` or `INCOMPLETE` into `DENIED`.
5. Block only when an independent authority/safety/provider constraint explicitly blocks the affected action, or when explicit negative evidence falsifies a required dependent predicate. Scope the block to that dependency.
6. Generate an epistemic verification receipt with SHA-256 hashes and timestamp when available, recording tier, evidence, counterevidence, unresolved debt, and any independent blocking source separately.

## Output contract

Produce `epistemic-verification-receipt.json` detailing the assigned epistemic tier, verification artifacts, SHA-256 digests, unresolved verification debt, and any independent authority/provider blocker. Never label the tier itself as Operator authorization.

## Local validation

The classifier passes when it reports the strongest evidence tier supported by observed state, refuses unsupported completion/readiness claims, preserves `UNKNOWN`/`INCOMPLETE` as non-authorizing epistemic states, and does not convert verification into pre-action permission. Enterprise deliverables may target $\ge \mathcal{L}_5$ as a quality/evidence objective without making that target a universal execution gate.

## Non-goals

Do not generate marketing or unverified claims. Do not permit non-functional stubs (`pass`, `return True`) to masquerade as working behavior. Do not manufacture Operator authorization, global stop conditions, or per-action approval requirements from evidence tiers.
