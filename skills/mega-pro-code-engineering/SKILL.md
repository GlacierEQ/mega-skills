---
name: mega-pro-code-engineering
description: "The Sovereign Master Code Engineering & Pro Genius Engine. Ties together Vercel Edge & AI Gateway, Supabase PGVector & Postgres RLS, APEX Durable Workflow Control Plane, Multi-Model Swarm Symphony, and Rosetta Polyglot Systems for production-grade, zero-stub engineering."
---

# 🏛️ MEGA-PRO-CODE-ENGINEERING — The Sovereign Master Engine

> *"Apex is precision, calculation, foresight, and flawless execution.  
> Take what exists, make it better. The wheel is knowledge; four wheels on a precision chassis is innovation.  
> Real engineering, real code, real genius. Zero magic numbers, zero superficial stubs, 100% mathematical and empirical proof."*

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           MEGA-PRO-CODE-ENGINEERING SYNAPSE                               │
├───────────────────────────────┬───────────────────────────┬───────────────────────────────┤
│       1. VERCEL & NEXT.JS     │   2. SUPABASE COLOSSAL    │     3. APEX CONTROL PLANE     │
│   Next.js 15+ App Router, RSC │ Postgres RLS, HNSW Vector │ 15-State Lifecycle, ChangeSets│
│   AI Gateway (OIDC, <20ms)    │ Deno Edge Functions, REST │ ECHO Hash Chaining, Readback  │
├───────────────────────────────┼───────────────────────────┼───────────────────────────────┤
│    4. MULTI-MODEL SWARM       │    5. ROSETTA POLYGLOT    │      6. HUMANIZED DX & DEV    │
│ 4-Phase Dialectic Pipeline    │ 51-Floor Systems Engine   │ Self-Documenting Architecture │
│ R1 ➔ Qwen ➔ V3 ➔ Gemini       │ Rust, Metal, eBPF, Go, Py │ Dev Fork Doctrine & Overlays  │
└───────────────────────────────┴───────────────────────────┴───────────────────────────────┘
```

---

## 💎 1. Vercel Cloud, Edge & AI Gateway Architecture
- **Unified AI Gateway with OIDC**: Use `ai@^6.0.0` with standard `"provider/model"` slugs. Auth via short-lived OIDC JWTs (`VERCEL_OIDC_TOKEN`), zero manual API key drift.
- **Failover Chains & Edge Caching**: Automatic sub-20ms failover (`order: ['anthropic', 'openai', 'bedrock']`) and edge response caching (`cacheControl: 'max-age=3600'`).
- **Next.js 15+ Invariants**: Server Component isolation, React Server Actions with optimistic concurrency, and strict CSP/HSTS headers.

---

## 🏛️ 2. Supabase Colossal Relational & PGVector Engine
- **Anti-BOLA / Anti-IDOR RLS Standard**: Every policy pairs role targeting with explicit ownership predicates:
  ```sql
  create policy "user_own_rows" on public.records for select to authenticated using ((select auth.uid()) = user_id);
  ```
- **HNSW PGVector Indexing**: Fast cosine distance search for AI agent memory and legal evidence retrieval:
  ```sql
  create index on public.evidence_vectors using hnsw (embedding vector_cosine_ops);
  ```
- **Security Invoker Views**: Always define views with `WITH (security_invoker = true)` in Postgres 15+ to obey table-level RLS.

---

## ⚡ 3. APEX Durable State Machine & Execution Invariant
- **The Supreme Execution Invariant**:
  $$\text{COMPLETE} \iff \text{mutation} + \text{readback} + (\text{expected\_delta} == \text{observed\_delta})$$
- **Two-Phase Compensating Transactions**: If any operation in a ChangeSet fails verification, transition to `COMPENSATING`, revert prior applied operations in reverse order, log a `ROLLED_BACK` receipt in the ECHO ledger, and safely halt with zero data loss.

---

## 🐝 4. Multi-Model Dialectic Swarm Symphony
1. **Phase 1: Reasoner** (DeepSeek R1 / o1 / o3-mini) $\to$ Architectural Blueprint & Invariant Proofs.
2. **Phase 2: Synthesizer** (Qwen 2.5 Coder 32B / GPT-5.4 / Claude Sonnet) $\to$ Production Code (zero stubs).
3. **Phase 3: Auditor** (DeepSeek V3 / Claude Sonnet) $\to$ Adversarial edge-case audit & vulnerability scan.
4. **Phase 4: Perception** (Gemini 2.5/3 Flash / Qwen-VL) $\to$ Multimodal & document evidence vectors.

---

## 🛠️ 5. Rosetta Polyglot Systems & Hardware Precision
- **Sub-microsecond IPC**: Cap'n Proto zero-copy serialization.
- **Apple Silicon GPU**: Swift Metal (`MSL`) unified memory compute.
- **Kernel Sandboxing**: eBPF in-kernel syscall sentinels.
- **Microservices**: Go lightweight concurrent daemons.
- **Safety Proofs**: Lean 4 truth invariants and Rust memory safety.

---

## 🔱 6. Dev Fork Doctrine & Modular Overlay Pattern
- **Pristine Upstream Base**: Core upstream code remains untouched and cleanly rebaseable.
- **Overlay Architecture**: Custom features, adapters, and multi-model bridges live in decoupled layers (`extensions/`, `adapters/`, `sidecars/`).
- **Automated Upstream Sync**: Weekly CI workflows pull upstream changes and require 100% green regression test runs before promoting to `origin/main`.

---

## 👑 7. Humanized Developer Experience & Engineering Elegance
- **Self-Documenting Code**: Code reads like clear technical prose with strict typing.
- **3-Point Actionable Diagnostics**: What failed $\to$ Why it failed $\to$ Exact command to fix it.
- **Zero Token Waste (Mega Token Saver)**: Maximum architectural leverage with minimal tokens burned. Execute directly, prove with tests, and ship clean.
