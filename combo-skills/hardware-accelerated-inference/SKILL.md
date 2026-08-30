---
name: hardware-accelerated-inference
description: 'Combo Skill: Hardware Accelerated Inference. Reusable capability chain.'
---

# Hardware Accelerated Inference

## Purpose and selection

Optimizing neural network inference across heterogeneous hardware (Apple Neural Engine, AWS Trainium, xAI Colossus, NVIDIA/MLIR).
Do **not** use when standard cloud api inference (openai, anthropic) where hardware execution is abstracted.

## Incremental value

Heterogeneous hardware inference orchestration: synthesizes ANE quantization, MoE attention routing, and Trainium execution into an empirically benchmarked inference profile.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `apple-ane-kv-quantizer` | Skill | Yes | Compile Apple Neural Engine KV-cache quantization kernels. | Model architecture definition, Target quantization budget | ANE_QUANTIZATION_PROFILE.json, Compiled CoreML/Metal kernels | Quantized weights achieve target compression without perplexity degradation. |
| 2 | `deepseek-mla-moe-sentinel` | Skill | Yes | Configure Multi-Head Latent Attention and Mixture-of-Experts routing. | ANE_QUANTIZATION_PROFILE.json, MoE routing topology | MLA_ROUTING_SPEC.json, Expert capacity allocations | Latent attention projections and expert dispatch latency under 2ms. |
| 3 | `openai-reasoning-kv-sentinel` | Skill | Yes | Optimize reasoning budget, context caching, and KV memory bounds. | MLA_ROUTING_SPEC.json, Context window target | KV_CACHE_BUDGET.json, Dynamic memory pool layout | KV memory footprint fits strictly within allocated hardware VRAM. |
| 4 | `aws-trainium-neuron-sentinel` | Skill | Yes | Profile and orchestrate NeuronCore execution pipelines on AWS Trainium. | KV_CACHE_BUDGET.json, Neuron compiler directives | NEURON_EXECUTION_GRAPH.json, Ring-orbit compilation artifacts | NeuronCore graph compilation passes with 100% operator coverage. |
| 5 | `quality-gate` | Skill | Yes | Benchmark Time-to-First-Token, tokens/sec, and memory footprint invariants. | NEURON_EXECUTION_GRAPH.json, Inference benchmark logs | HARDWARE_INFERENCE_BENCHMARK.md, Hardware certification receipt | TTFT latency < 50ms and throughput exceeds SLA baseline across all test batches. |

## Ordered execution

1. **Step 1 — `apple-ane-kv-quantizer`**: Consumes Model architecture definition, Target quantization budget, produces ANE_QUANTIZATION_PROFILE.json, Compiled CoreML/Metal kernels, and satisfies: Quantized weights achieve target compression without perplexity degradation.
2. **Step 2 — `deepseek-mla-moe-sentinel`**: Consumes ANE_QUANTIZATION_PROFILE.json, MoE routing topology, produces MLA_ROUTING_SPEC.json, Expert capacity allocations, and satisfies: Latent attention projections and expert dispatch latency under 2ms.
3. **Step 3 — `openai-reasoning-kv-sentinel`**: Consumes MLA_ROUTING_SPEC.json, Context window target, produces KV_CACHE_BUDGET.json, Dynamic memory pool layout, and satisfies: KV memory footprint fits strictly within allocated hardware VRAM.
4. **Step 4 — `aws-trainium-neuron-sentinel`**: Consumes KV_CACHE_BUDGET.json, Neuron compiler directives, produces NEURON_EXECUTION_GRAPH.json, Ring-orbit compilation artifacts, and satisfies: NeuronCore graph compilation passes with 100% operator coverage.
5. **Step 5 — `quality-gate`**: Consumes NEURON_EXECUTION_GRAPH.json, Inference benchmark logs, produces HARDWARE_INFERENCE_BENCHMARK.md, Hardware certification receipt, and satisfies: TTFT latency < 50ms and throughput exceeds SLA baseline across all test batches.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `apple-ane-kv-quantizer` | `deepseek-mla-moe-sentinel` | ANE_QUANTIZATION_PROFILE.json | MLA_ROUTING_SPEC.json | quantization-engineer |
| `deepseek-mla-moe-sentinel` | `openai-reasoning-kv-sentinel` | MLA_ROUTING_SPEC.json | KV_CACHE_BUDGET.json | moe-specialist |
| `openai-reasoning-kv-sentinel` | `aws-trainium-neuron-sentinel` | KV_CACHE_BUDGET.json | NEURON_EXECUTION_GRAPH.json | kv-architect |
| `aws-trainium-neuron-sentinel` | `quality-gate` | NEURON_EXECUTION_GRAPH.json | HARDWARE_INFERENCE_BENCHMARK.md | neuron-engineer |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Empirical latency profiling measurements (TTFT, tokens/sec).
- VRAM and memory allocation telemetry receipts.
- Perplexity verification benchmarks confirming zero loss of fidelity.

Risk boundaries:
- Zero out-of-memory kernel crashes under maximum concurrency.
- Strict thermal and compute budget adherence on local Apple Silicon.

## Quality gates

- TTFT meets target SLA (<50ms).
- Zero memory leaks across 10,000 token execution loops.

## Compound output

**Artifact:** `HARDWARE_INFERENCE_BENCHMARK.md`

**Ready for Mega Skill integration when:**

1. Hardware inference benchmark achieves target throughput.
2. Quality gate certifies zero OOM or accuracy regression.
