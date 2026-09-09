# Forward Deployed Engineering — Estate Evidence Audit

**Date:** 2026-09-09 HST  
**Purpose:** Ground Casey Barton / GlacierEQ FDE positioning in inspected source-bearing engineering artifacts rather than generic AI-role language.

## Executive conclusion

The estate's strongest recurring engineering pattern is not generic "AI orchestration." It is **operationalization under ambiguity**:

1. translate an ambiguous or domain-specific problem into explicit state, contracts, constraints, and authority boundaries;
2. build deterministic or bounded execution/decision machinery;
3. preserve failure, deferral, dissent, stale-state, and non-completion instead of smoothing them away;
4. bind claims and state transitions to receipts, hashes, exact revisions, tests, or provider readback;
5. separate proposal, authorization, execution, persistence, verification, deployment, and observed operation;
6. extract reusable patterns across domains, runtimes, languages, and external-system boundaries.

That pattern is strongly aligned to Forward Deployed Engineering: discover reality, model the operational constraint, build the system, integrate the boundary, verify behavior, and generalize the mechanism.

## Tier A — strongest public FDE proof

### GlacierEQ/apex-control-plane

**Mechanisms inspected:** fail-closed orchestration; known-state reuse; mission-outcome fidelity; operation-class preservation; worker authority; dynamic source-awareness watermarks; append-only evaluation receipts; dispatch fences; stale-action reevaluation; external preflight.

**High-value FDE signal:** prevents an action derived from stale cached intent from dispatching after newer source-bearing reality arrives. The action queue is fenced by awareness state rather than trusting an old plan.

**Positioning:** production-minded AI/control-plane architecture, continuity, state integrity, runtime safety, dynamic reevaluation, evidence-bearing execution.

### GlacierEQ/anthropic-safety-monitor

**Mechanisms inspected:** deterministic ToolCall review; ALLOW / CONFIRM / DENY; stable rule IDs; shell-chain segmentation; wrapper normalization; critical-path normalization; confirmation boundaries; hash-bound transcript receipts; predecessor chaining; tamper detection; bounded/defused JUnit verification.

**Evidence:** exact promotion reports 51 tests per Python 3.11/3.12/3.13, 153 total, zero failures/errors/skips.

**Positioning:** agent tool safety boundary, human-directed execution, adversarial parsing, deterministic auditability.

### GlacierEQ/the-tower-of-babel

**Mechanisms inspected:** executable technology placement; 40 technology floors; build/test/benchmark/formal-proof gates; explicit blockers; versioned cross-language interfaces; deterministic evidence; agent-readable selection contracts.

**Flagship boundary:** TypeScript ingress -> ProtoJSON contract -> Python planner -> Rust decision governor -> Go telemetry -> SQL state -> WebAssembly sandbox -> Lean 4 receipt-chain invariant -> receipt.

**Positioning:** heterogeneous systems architecture, polyglot interoperability, choosing technology by workload/safety/proof boundary rather than novelty.

### GlacierEQ/glaciereq-mcp-stack

**Mechanisms inspected:** explicit separation of registration from execution authority; execution allow-list; write mutation gate; fail-closed dispatch; credential-gated stdio MCP packages for GitHub, Asana, Confluence, Supabase, Neo4j; shared environment/logging/retry surfaces.

**Positioning:** MCP integration architecture, authority boundaries, connector composition, truthful separation of implemented vs connected/deployed state.

### GlacierEQ/microsoft-identity-zero-trust

**Mechanisms inspected:** zero-trust decision policy; exact audience/scope/lifetime/source-bound workload identity envelope; action-policy-derived scopes and modes; autonomous vs delegated principal distinction; DENY / STEP_UP / ALLOW; hash-bound policy receipts; fail-closed unknown action assignment.

**Positioning:** least privilege for agentic systems, workload identity, policy-derived authorization, enterprise security architecture.

### GlacierEQ/adobe-creative-provenance-gate

**Mechanisms inspected in source:** content-addressed source claims; SHA-256 lineage; ordered transformations; tool/model identity; rights and derivative constraints; cost budget; editability preservation; brand rules; authority expiry; output lineage membership; tamper-evident receipts.

**Positioning:** converts a messy creative-enterprise provenance problem into an executable policy and lineage engine. This is a strong forward-deployed problem-decomposition example because it starts from a real workflow risk rather than an AI demo.

### GlacierEQ/amd-hetero-placement-contract

**Mechanisms inspected in source:** workload/topology normalization; hard feasibility rejection; available compute under utilization; available memory; bandwidth; latency; privacy; power; required features; budget; target availability; deterministic multi-factor ranking; explicit REFUSE when no feasible target.

**Positioning:** infrastructure/workload placement under heterogeneous constraints; strong example of converting operational requirements into deterministic deployment selection.

### GlacierEQ/spacex-autonomy

**Mechanisms inspected:** deterministic autonomy-mode policy and hysteresis; alpha-beta estimation; bounded controller; weighted peer fusion; GO/HOLD mission-thread quorum with explicit veto and hold reasons; Go phase-transition and abort-threshold state machine with concurrency tests.

**Boundary:** simulation only; no vehicle authority.

**Positioning:** state-machine design, bounded autonomy, conflicting-signal preservation, multi-language domain modeling.

### GlacierEQ/xai-colossus-cooling

**Mechanisms inspected:** thermal node/rack/zone models; threshold classification; zone aggregation; thermal-budget checks; moving-baseline anomaly detection; emergency decision modules; async controller dispatch in simulation.

**Boundary:** simulation only; no real GPU telemetry or cooling hardware authority.

**Positioning:** domain translation from facility telemetry to explicit control decisions, with honest simulation/production boundary.

### GlacierEQ/nvidia-gpu-health

**Mechanisms inspected:** deterministic Python GPU-health policy; C11 link/ECC evaluator; rack-level integrity quorum; explicit NOMINAL/WARNING/CRITICAL states; review-candidate identification; SHA-bound local receipts.

**Positioning:** infrastructure health modeling and cross-language systems boundaries.

## Tier A — strongest internal/private proof

### GlacierEQ/computer-user

**Mechanisms inspected:** persistent HTTP execution kernel; durable SQLite task queue; worker; capability registry; connector dispatch; health/readiness; task/receipt readback; installed execution doctor; optional browser boundary; container/systemd/launchd deployment assets; raw-secret rejection; hash-only action receipts.

**Core runtime:** caller -> invocation -> capability resolution -> durable queue -> connector execution -> verification -> receipt -> readback.

**Why it matters:** this is one of the estate's clearest demonstrations that architecture is subordinate to actual executed work and durable readback. It is highly relevant to FDE engineering but should remain private unless a public-safe derivative is deliberately created.

### Pro-DOCTOR-STRANGE runtime receipt

Previously verified internally as a genuine external model-backed execution receipt with source hash, output hashes, provider identity, correlation ID, latency, raw output, and explicit anti-fabrication boundaries. This is valuable production-LLM evidence but not public-safe by default.

## Tier A candidate — current source outruns public README

### GlacierEQ/xai-colossus-security

The README still describes the event bus as experimental, but current source has advanced:

- stable `src/security_event_bus.py` import surface;
- Supabase-backed audit sink;
- runtime adapter that writes a connector heartbeat before activation;
- fail-closed startup on heartbeat rejection;
- `require_persistence=True` event bus;
- CRITICAL-only subscription into a P0 dispatcher;
- dispatch only after durable persistence;
- MCP sender adapter that transmits structured event payload without embedding provider credentials in event state.

This should be re-evaluated for public promotion after exact-head verification/readback is re-established. Do not let the stale README suppress stronger current source, but do not claim CI/runtime proof that has not been freshly read back.

## Tier B — strong functional or research mechanisms, not top Featured proof yet

### GlacierEQ/openai-reasoning-kv-sentinel

Real local reasoning-record retention policy with Shannon entropy, anchors, tail retention, optional ONNX/NumPy scoring, bounded cache-count pressure, plus digest-bound pointer handoff with required-pointer failure and supersession. Useful context/memory systems evidence. It explicitly does not mutate transformer KV tensors or integrate a model server.

### GlacierEQ/deepmind-tpu-mesh-optimizer

Useful deterministic mesh scenario planning and a strong evidence-promotion fence: MODELED -> LOCAL_TESTED -> COMPILED -> HARDWARE_MEASURED. Shows accelerator-topology reasoning and unusually disciplined claim separation, but remains modeled rather than hardware-measured.

### GlacierEQ/anthropic-agent-coordinator

A real dependency-aware DAG scheduler with shared token budget, aggregate role capacities, full-funding semantics, explicit deferrals, assignment waves, cycle/malformed-input failure, and assignment-bound tool proposals. Historical exact-revision proof exists (62/62), but current head is explicitly pending fresh exact-SHA verification. Strong mechanism; proof freshness is the current limiter.

## Reference / supporting mechanisms — useful, but should not lead the profile

- `spacex-mission-thread-quorum`: compact GO/HOLD quorum reference; useful concept, smaller proof surface than `spacex-autonomy`.
- `anduril-lattice-dissent-freeze`: high-severity dissent freezes a recommendation; useful bounded-consensus reference.
- `anduril-sensor-health-quorum`: peer-health trust determines voting eligibility; useful reference mechanism.

These are good supporting examples of a recurring dissent/quorum/fail-closed design instinct, not primary portfolio anchors.

## Explicitly do not lead with these

### GlacierEQ/agentclaw-extension

The product surface is broad and the command registry is real, but source inspection of `src/features/agentIntelligence/index.ts` shows several advertised agent features currently terminate in VS Code UI messages and audit-log records rather than performing the deep execution implied by the README. Treat as product/UI scaffolding and a capability-development surface, not equivalent to the execution kernel or tested control-plane systems.

### GlacierEQ/AEON-777

Contains sensitive legal/case material and legacy probabilistic legal claims. Keep it outside public career projection. The legal domain may demonstrate operational systems thinking privately, but the repository is neither the right public evidence surface nor a career identity anchor.

### GlacierEQ/antigravity-cli

Potentially relevant multi-model/upstream-overlay work, but this audit did not establish runtime proof for its broad provider/model/subagent claims. Keep as candidate until source and execution receipts are reviewed.

## The actual engineering thesis

The most defensible public narrative is:

> Casey Barton builds the operating layer between AI reasoning and consequential real-world action. He turns ambiguous workflows into explicit state machines, authority boundaries, integration contracts, failure semantics, and evidence-bearing execution paths; then generalizes the successful mechanism across domains and runtimes.

That is stronger and more accurate than generic labels such as "AI enthusiast," "prompt engineer," or even "agent orchestrator."

## Repeated design signatures found across unrelated domains

1. **Proposal is not execution.** Proposed tool calls, security responses, deployment targets, and mission votes remain separate from executed state.
2. **Failure is first-class state.** Deferrals, vetoes, stale source state, missing providers, blocked hardware/toolchains, insufficient capacity, and no-feasible-target states are preserved explicitly.
3. **Authority is typed.** Registration, recommendation, confirmation, delegated human authority, autonomous workload identity, and execution authority are not collapsed.
4. **Evidence is monotonic and bounded.** TEST, runtime, provider, deployment, and hardware claims require their own proof; one level cannot self-promote to another.
5. **Inputs are adversarially validated.** Non-finite values, malformed graphs, duplicate IDs, unsafe wrappers, digest mismatches, stale pointers, wrong scopes, and unsupported transitions fail closed.
6. **Receipts are architectural objects.** SHA-256, exact revision binding, predecessor chains, provider references, evaluation receipts, and readback appear across domains.
7. **Cross-language boundaries are intentional.** Python, TypeScript, Rust, Go, C/C++, SQL, WebAssembly, Lean and other technologies are assigned responsibilities by operational fit rather than portfolio decoration.
8. **Domain names change; the systems instinct does not.** Thermal orchestration, autonomy, creative provenance, identity, workload placement, security events, agent tools, and continuity repeatedly collapse into observable state + constraints + bounded decision/execution + verification.

## FDE fit assessment

### Already strongly evidenced

- AI/system architecture from ambiguous requirements
- hands-on production-minded engineering
- agent/tool/MCP architecture
- enterprise integration boundaries
- authority/security design
- evaluation, observability, failure semantics
- bounded autonomy and human control
- high-agency problem decomposition
- reusable pattern extraction
- heterogeneous/runtime technology placement

### Still distinct and not to be fabricated

- real external customer discovery
- real customer deployment/adoption lifecycle
- independently measured customer/business outcome

Those gaps should be closed through genuine field engagements, not by relabeling internal company research or simulations as customer work.

## Public positioning recommendation

**Primary lane:** Forward Deployed Engineering  
**Professional identity:** Forward Deployed AI Architect  
**Technical center of gravity:** reliable agentic systems, AI control planes, MCP/tool integration, bounded execution, evidence/observability, heterogeneous systems.

### Better one-line thesis

> Forward Deployed AI Architect building reliable agentic systems that turn ambiguous operational problems into bounded, integrated, verifiable execution.

### Recruiter proof order

1. APEX Control Plane — dynamic reality-aware execution and mission-outcome fidelity
2. Anthropic Safety Monitor — deterministic tool-use safety + hash-bound transcripts
3. Tower of Babel — executable technology placement and polyglot proof system
4. MCP Stack — governed tool integration and mutation boundaries
5. Microsoft Identity Zero Trust — policy-derived agent/workload authorization
6. Adobe Creative Provenance Gate — workflow-specific provenance engine
7. AMD Heterogeneous Placement — constrained workload placement/refusal engine
8. SpaceX Autonomy — bounded autonomy + quorum/state-machine simulation
9. xAI Cooling / Security — domain-specific operational control and runtime boundary work
10. NVIDIA GPU Health — infrastructure integrity modeling

The portfolio should show breadth only after it establishes this coherent engineering through-line. The goal is not to hide the estate; it is to make the estate legible without reducing it.