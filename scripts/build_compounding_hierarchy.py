#!/usr/bin/env python3
"""
Synthesize and register high-leverage Combo Skills and Mega Skills
that hierarchically tie complementary atomic skills together.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
COMBOS_JSON = REGISTRY_DIR / "combo-skills.json"
MEGAS_JSON = REGISTRY_DIR / "mega-skills.json"
COMBOS_DIR = ROOT / "combo-skills"
MEGAS_DIR = ROOT / "mega-skills"

# ------------------------------------------------------------------------------
# 1. NEW HIGH-BENEFIT COMBO SKILLS DEFINITIONS
# ------------------------------------------------------------------------------
NEW_COMBOS = [
    {
        "id": "autonomous-agent-foundry",
        "display_name": "Autonomous Agent Foundry",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "combo-skills/autonomous-agent-foundry",
        "entrypoint": "combo-skills/autonomous-agent-foundry/COMBO.md",
        "selection": {
            "use_when": [
                "Designing, equipping, testing, and benchmarking an autonomous AI agent for production.",
                "Engineering multi-turn memory systems with behavioral test verification."
            ],
            "do_not_use_when": [
                "Simple one-off prompt adjustments without tool use or memory requirements.",
                "Ad-hoc script execution without agent state architectures."
            ]
        },
        "members": [
            {"id": "ai-agents-architect", "kind": "skill", "role": "Architect agent role, tool schemas, and decision planning loops.", "required": True},
            {"id": "agent-memory-mcp", "kind": "skill", "role": "Integrate persistent searchable episodic and semantic memory.", "required": True},
            {"id": "agent-evaluation", "kind": "skill", "role": "Execute statistical benchmarks, behavioral tests, and adversarial probes.", "required": True},
            {"id": "quality-gate", "kind": "skill", "role": "Validate performance thresholds, accuracy, and zero regression bounds.", "required": True}
        ],
        "execution": {
            "ordered_steps": [
                {
                    "step": 1,
                    "member_id": "ai-agents-architect",
                    "consumes": ["Agent operational mandate", "Tool capability requirements"],
                    "produces": ["AGENT_ARCHITECTURE_SPEC.md", "Tool integration schemas"],
                    "validation": "Agent roles, capabilities, and tool boundaries are formally specified."
                },
                {
                    "step": 2,
                    "member_id": "agent-memory-mcp",
                    "consumes": ["AGENT_ARCHITECTURE_SPEC.md", "Memory persistence parameters"],
                    "produces": ["AGENT_MEMORY_CONFIGURATION.json", "Memory retrieval index"],
                    "validation": "Searchable memory endpoints pass read/write latency and recall tests."
                },
                {
                    "step": 3,
                    "member_id": "agent-evaluation",
                    "consumes": ["AGENT_ARCHITECTURE_SPEC.md", "AGENT_MEMORY_CONFIGURATION.json", "Evaluation test suite"],
                    "produces": ["AGENT_EVALUATION_REPORT.json", "Accuracy & robustness metrics"],
                    "validation": "Agent achieves >95% benchmark pass rate with zero tool-call hallucinations."
                },
                {
                    "step": 4,
                    "member_id": "quality-gate",
                    "consumes": ["AGENT_EVALUATION_REPORT.json", "Agent deployment bundle"],
                    "produces": ["AGENT_FOUNDRY_RELEASE_PACKET.md", "Quality gate certification"],
                    "validation": "All gate criteria pass with zero critical regressions or security vulnerabilities."
                }
            ]
        },
        "integration": {
            "handoffs": [
                {
                    "from_member": "ai-agents-architect",
                    "to_member": "agent-memory-mcp",
                    "required_inputs": ["AGENT_ARCHITECTURE_SPEC.md"],
                    "accepted_outputs": ["AGENT_MEMORY_CONFIGURATION.json"],
                    "failure_owner": "agent-architect"
                },
                {
                    "from_member": "agent-memory-mcp",
                    "to_member": "agent-evaluation",
                    "required_inputs": ["AGENT_MEMORY_CONFIGURATION.json"],
                    "accepted_outputs": ["AGENT_EVALUATION_REPORT.json"],
                    "failure_owner": "memory-specialist"
                },
                {
                    "from_member": "agent-evaluation",
                    "to_member": "quality-gate",
                    "required_inputs": ["AGENT_EVALUATION_REPORT.json"],
                    "accepted_outputs": ["AGENT_FOUNDRY_RELEASE_PACKET.md"],
                    "failure_owner": "eval-engineer"
                }
            ],
            "evidence_requirements": [
                "Deterministic evaluation logs with confidence intervals.",
                "Verified memory retrieval latency (<15ms) and recall accuracy (>92%).",
                "Tool-call parameter validation receipts."
            ],
            "risk_boundaries": [
                "Zero unvetted system command execution.",
                "Zero persistent credential exposure in memory graphs."
            ],
            "quality_gates": [
                "Agent evaluation benchmark score >= 95%.",
                "All memory write/read assertions pass unit testing."
            ],
            "state_updates": [
                "Record agent release packet in durable evidence register.",
                "Publish agent configuration to local runtime registry."
            ]
        },
        "compounding": {
            "inherits": [
                "ai-agents-architect architectural patterns",
                "agent-memory-mcp persistence protocols",
                "agent-evaluation statistical test harness",
                "quality-gate verification standards"
            ],
            "adds": "End-to-end agent lifecycle synthesis: unites architecture, persistent memory, and statistical evaluation into a deployable certified agent packet.",
            "compound_artifact": "AGENT_FOUNDRY_RELEASE_PACKET.md",
            "next_layer_ready_when": [
                "The agent bundle is certified by quality-gate.",
                "Memory retrieval and evaluation reports are attached."
            ]
        }
    },
    {
        "id": "architectural-refactoring-engine",
        "display_name": "Architectural Refactoring Engine",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "combo-skills/architectural-refactoring-engine",
        "entrypoint": "combo-skills/architectural-refactoring-engine/COMBO.md",
        "selection": {
            "use_when": [
                "Elevating legacy modules to production standards with zero regressions.",
                "Restructuring multi-file architectures, breaking cycles, and removing code smells."
            ],
            "do_not_use_when": [
                "Minor single-line typo or lint formatting changes.",
                "Adding net-new domain features without modifying existing architectures."
            ]
        },
        "members": [
            {"id": "architecture", "kind": "skill", "role": "Analyze system design, evaluate trade-offs, and generate Architecture Decision Records.", "required": True},
            {"id": "clean-code", "kind": "skill", "role": "Refactor implementation to pragmatic standards with zero bloat and explicit typing.", "required": True},
            {"id": "ast-repair-core", "kind": "skill", "role": "Parse AST tracebacks, locate structural defects, and apply surgical patches.", "required": True},
            {"id": "code-review-checklist", "kind": "skill", "role": "Execute comprehensive audit for security, maintainability, and concurrency safety.", "required": True},
            {"id": "quality-gate", "kind": "skill", "role": "Verify test assertion pass rates, typecheck completion, and invariant adherence.", "required": True}
        ],
        "execution": {
            "ordered_steps": [
                {
                    "step": 1,
                    "member_id": "architecture",
                    "consumes": ["Target codebase directory", "Refactoring requirements"],
                    "produces": ["ARCHITECTURE_DECISION_RECORD.md", "Target interface contracts"],
                    "validation": "ADR clearly defines trade-offs, interface boundaries, and invariant requirements."
                },
                {
                    "step": 2,
                    "member_id": "clean-code",
                    "consumes": ["ARCHITECTURE_DECISION_RECORD.md", "Existing source files"],
                    "produces": ["Refactored source tree", "Strict typing annotations"],
                    "validation": "All magic numbers removed, type coverage 100%, cyclomatic complexity bounded."
                },
                {
                    "step": 3,
                    "member_id": "ast-repair-core",
                    "consumes": ["Refactored source tree", "Compiler/test execution logs"],
                    "produces": ["Synthesized AST patches", "Green compiler receipts"],
                    "validation": "Zero syntax errors, zero unresolved imports, 100% clean AST parse."
                },
                {
                    "step": 4,
                    "member_id": "code-review-checklist",
                    "consumes": ["Refactored source tree", "Compiler receipts"],
                    "produces": ["CODE_REVIEW_AUDIT.md", "Remediation directives"],
                    "validation": "Security, performance, and maintainability dimensions meet staff engineer standards."
                },
                {
                    "step": 5,
                    "member_id": "quality-gate",
                    "consumes": ["CODE_REVIEW_AUDIT.md", "Test suite execution receipts"],
                    "produces": ["ARCHITECTURAL_REFACTORING_RECORD.md", "Release approval"],
                    "validation": "100% test pass rate with zero behavioral regressions."
                }
            ]
        },
        "integration": {
            "handoffs": [
                {
                    "from_member": "architecture",
                    "to_member": "clean-code",
                    "required_inputs": ["ARCHITECTURE_DECISION_RECORD.md"],
                    "accepted_outputs": ["Refactored source tree"],
                    "failure_owner": "system-architect"
                },
                {
                    "from_member": "clean-code",
                    "to_member": "ast-repair-core",
                    "required_inputs": ["Refactored source tree"],
                    "accepted_outputs": ["Synthesized AST patches"],
                    "failure_owner": "lead-coder"
                },
                {
                    "from_member": "ast-repair-core",
                    "to_member": "code-review-checklist",
                    "required_inputs": ["Synthesized AST patches"],
                    "accepted_outputs": ["CODE_REVIEW_AUDIT.md"],
                    "failure_owner": "ast-engineer"
                },
                {
                    "from_member": "code-review-checklist",
                    "to_member": "quality-gate",
                    "required_inputs": ["CODE_REVIEW_AUDIT.md"],
                    "accepted_outputs": ["ARCHITECTURAL_REFACTORING_RECORD.md"],
                    "failure_owner": "auditor"
                }
            ],
            "evidence_requirements": [
                "Architecture Decision Record documenting trade-offs.",
                "Static AST verification logs with zero parse errors.",
                "Comprehensive code review audit report."
            ],
            "risk_boundaries": [
                "Zero breaking changes to external public API contracts.",
                "Zero untested code paths committed to main branch."
            ],
            "quality_gates": [
                "Pytest / unit test pass rate = 100%.",
                "Strict typing validation with zero type errors."
            ],
            "state_updates": [
                "Update repository ADR catalog with new decisions.",
                "Emit refactoring verification receipt to evidence register."
            ]
        },
        "compounding": {
            "inherits": [
                "architecture ADR patterns",
                "clean-code concise standards",
                "ast-repair-core surgical patch engine",
                "code-review-checklist multi-dimensional audit",
                "quality-gate verification gates"
            ],
            "adds": "Closed-loop architectural transformation: connects high-level ADR design with clean implementation, automated AST patching, and peer-grade code review.",
            "compound_artifact": "ARCHITECTURAL_REFACTORING_RECORD.md",
            "next_layer_ready_when": [
                "Refactored code achieves 100% test pass rate.",
                "Code review checklist flags zero high or critical risks."
            ]
        }
    },
    {
        "id": "secure-service-deployment",
        "display_name": "Secure Service Deployment",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "combo-skills/secure-service-deployment",
        "entrypoint": "combo-skills/secure-service-deployment/COMBO.md",
        "selection": {
            "use_when": [
                "Containerizing and deploying microservices, MCP servers, or background APIs.",
                "Establishing secure cloud deployments with secret hygiene and automated health probes."
            ],
            "do_not_use_when": [
                "Local interactive script execution without containerization or networking.",
                "Static text or documentation drafting."
            ]
        },
        "members": [
            {"id": "api-integration", "kind": "skill", "role": "Specify typed API interfaces, retry backoff, and webhook listeners.", "required": True},
            {"id": "docker-devops", "kind": "skill", "role": "Author multi-stage Dockerfiles, compose environments, and registry pipelines.", "required": True},
            {"id": "security-review", "kind": "skill", "role": "Execute OWASP security review, credential sanitization, and vulnerability scanning.", "required": True},
            {"id": "mcp-master-server", "kind": "skill", "role": "Register and coordinate MCP tool endpoints with health watchdogs.", "required": True},
            {"id": "quality-gate", "kind": "skill", "role": "Validate container health, runtime latency, and cryptographic provenance.", "required": True}
        ],
        "execution": {
            "ordered_steps": [
                {
                    "step": 1,
                    "member_id": "api-integration",
                    "consumes": ["Service functional spec", "Protocol schemas"],
                    "produces": ["API_INTERFACE_SPEC.json", "Client SDK stubs"],
                    "validation": "OpenAPI / MCP protocol schemas are fully typed and validated."
                },
                {
                    "step": 2,
                    "member_id": "docker-devops",
                    "consumes": ["API_INTERFACE_SPEC.json", "Service source code"],
                    "produces": ["Dockerfile", "docker-compose.yml", "Container image digest"],
                    "validation": "Container builds successfully with multi-stage layer caching."
                },
                {
                    "step": 3,
                    "member_id": "security-review",
                    "consumes": ["Dockerfile", "docker-compose.yml", "Environment secrets"],
                    "produces": ["SECURITY_AUDIT_REPORT.md", "Air-gap credential manifest"],
                    "validation": "Zero baked-in secrets, zero high/critical CVEs in base images."
                },
                {
                    "step": 4,
                    "member_id": "mcp-master-server",
                    "consumes": ["API_INTERFACE_SPEC.json", "Container runtime configuration"],
                    "produces": ["MCP_REGISTRATION_MANIFEST.json", "Healthcheck watchdog"],
                    "validation": "MCP endpoints discoverable and responsive to protocol pings."
                },
                {
                    "step": 5,
                    "member_id": "quality-gate",
                    "consumes": ["SECURITY_AUDIT_REPORT.md", "MCP_REGISTRATION_MANIFEST.json"],
                    "produces": ["SERVICE_DEPLOYMENT_MANIFEST.md", "Production signoff"],
                    "validation": "End-to-end container healthcheck passes with bounded latency."
                }
            ]
        },
        "integration": {
            "handoffs": [
                {
                    "from_member": "api-integration",
                    "to_member": "docker-devops",
                    "required_inputs": ["API_INTERFACE_SPEC.json"],
                    "accepted_outputs": ["Dockerfile", "docker-compose.yml"],
                    "failure_owner": "api-engineer"
                },
                {
                    "from_member": "docker-devops",
                    "to_member": "security-review",
                    "required_inputs": ["Dockerfile", "docker-compose.yml"],
                    "accepted_outputs": ["SECURITY_AUDIT_REPORT.md"],
                    "failure_owner": "devops-engineer"
                },
                {
                    "from_member": "security-review",
                    "to_member": "mcp-master-server",
                    "required_inputs": ["SECURITY_AUDIT_REPORT.md"],
                    "accepted_outputs": ["MCP_REGISTRATION_MANIFEST.json"],
                    "failure_owner": "secops-auditor"
                },
                {
                    "from_member": "mcp-master-server",
                    "to_member": "quality-gate",
                    "required_inputs": ["MCP_REGISTRATION_MANIFEST.json"],
                    "accepted_outputs": ["SERVICE_DEPLOYMENT_MANIFEST.md"],
                    "failure_owner": "mcp-architect"
                }
            ],
            "evidence_requirements": [
                "Cryptographic SHA-256 container image digest.",
                "Automated vulnerability scan results with zero high/critical issues.",
                "Live healthcheck ping verification receipt."
            ],
            "risk_boundaries": [
                "Zero secrets or sensitive API keys committed or baked into images.",
                "Strict container isolation with non-root runtime users."
            ],
            "quality_gates": [
                "Container boots within 5 seconds and passes healthcheck.",
                "Security review confirms 100% credential air-gapping."
            ],
            "state_updates": [
                "Record deployment manifest in global service catalog.",
                "Update MCP gateway routing configuration."
            ]
        },
        "compounding": {
            "inherits": [
                "api-integration interface definitions",
                "docker-devops container orchestration",
                "security-review vulnerability auditing",
                "mcp-master-server routing coordination",
                "quality-gate production verification"
            ],
            "adds": "Unified secure deployment pipeline: integrates API typing, multi-stage containerization, OWASP security scanning, and MCP registration into a single certified release manifest.",
            "compound_artifact": "SERVICE_DEPLOYMENT_MANIFEST.md",
            "next_layer_ready_when": [
                "Container healthcheck passes with HTTP 200 / MCP ready status.",
                "Security review certifies zero credential leaks."
            ]
        }
    },
    {
        "id": "hardware-accelerated-inference",
        "display_name": "Hardware Accelerated Inference",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "combo-skills/hardware-accelerated-inference",
        "entrypoint": "combo-skills/hardware-accelerated-inference/COMBO.md",
        "selection": {
            "use_when": [
                "Optimizing neural network inference across heterogeneous hardware (Apple Neural Engine, AWS Trainium, xAI Colossus, NVIDIA/MLIR).",
                "Evaluating KV-cache quantization, MoE expert routing, and latency benchmarks."
            ],
            "do_not_use_when": [
                "Standard cloud API inference (OpenAI, Anthropic) where hardware execution is abstracted.",
                "Non-machine-learning application logic."
            ]
        },
        "members": [
            {"id": "apple-ane-kv-quantizer", "kind": "skill", "role": "Compile Apple Neural Engine KV-cache quantization kernels.", "required": True},
            {"id": "deepseek-mla-moe-sentinel", "kind": "skill", "role": "Configure Multi-Head Latent Attention and Mixture-of-Experts routing.", "required": True},
            {"id": "openai-reasoning-kv-sentinel", "kind": "skill", "role": "Optimize reasoning budget, context caching, and KV memory bounds.", "required": True},
            {"id": "aws-trainium-neuron-sentinel", "kind": "skill", "role": "Profile and orchestrate NeuronCore execution pipelines on AWS Trainium.", "required": True},
            {"id": "quality-gate", "kind": "skill", "role": "Benchmark Time-to-First-Token, tokens/sec, and memory footprint invariants.", "required": True}
        ],
        "execution": {
            "ordered_steps": [
                {
                    "step": 1,
                    "member_id": "apple-ane-kv-quantizer",
                    "consumes": ["Model architecture definition", "Target quantization budget"],
                    "produces": ["ANE_QUANTIZATION_PROFILE.json", "Compiled CoreML/Metal kernels"],
                    "validation": "Quantized weights achieve target compression without perplexity degradation."
                },
                {
                    "step": 2,
                    "member_id": "deepseek-mla-moe-sentinel",
                    "consumes": ["ANE_QUANTIZATION_PROFILE.json", "MoE routing topology"],
                    "produces": ["MLA_ROUTING_SPEC.json", "Expert capacity allocations"],
                    "validation": "Latent attention projections and expert dispatch latency under 2ms."
                },
                {
                    "step": 3,
                    "member_id": "openai-reasoning-kv-sentinel",
                    "consumes": ["MLA_ROUTING_SPEC.json", "Context window target"],
                    "produces": ["KV_CACHE_BUDGET.json", "Dynamic memory pool layout"],
                    "validation": "KV memory footprint fits strictly within allocated hardware VRAM."
                },
                {
                    "step": 4,
                    "member_id": "aws-trainium-neuron-sentinel",
                    "consumes": ["KV_CACHE_BUDGET.json", "Neuron compiler directives"],
                    "produces": ["NEURON_EXECUTION_GRAPH.json", "Ring-orbit compilation artifacts"],
                    "validation": "NeuronCore graph compilation passes with 100% operator coverage."
                },
                {
                    "step": 5,
                    "member_id": "quality-gate",
                    "consumes": ["NEURON_EXECUTION_GRAPH.json", "Inference benchmark logs"],
                    "produces": ["HARDWARE_INFERENCE_BENCHMARK.md", "Hardware certification receipt"],
                    "validation": "TTFT latency < 50ms and throughput exceeds SLA baseline across all test batches."
                }
            ]
        },
        "integration": {
            "handoffs": [
                {
                    "from_member": "apple-ane-kv-quantizer",
                    "to_member": "deepseek-mla-moe-sentinel",
                    "required_inputs": ["ANE_QUANTIZATION_PROFILE.json"],
                    "accepted_outputs": ["MLA_ROUTING_SPEC.json"],
                    "failure_owner": "quantization-engineer"
                },
                {
                    "from_member": "deepseek-mla-moe-sentinel",
                    "to_member": "openai-reasoning-kv-sentinel",
                    "required_inputs": ["MLA_ROUTING_SPEC.json"],
                    "accepted_outputs": ["KV_CACHE_BUDGET.json"],
                    "failure_owner": "moe-specialist"
                },
                {
                    "from_member": "openai-reasoning-kv-sentinel",
                    "to_member": "aws-trainium-neuron-sentinel",
                    "required_inputs": ["KV_CACHE_BUDGET.json"],
                    "accepted_outputs": ["NEURON_EXECUTION_GRAPH.json"],
                    "failure_owner": "kv-architect"
                },
                {
                    "from_member": "aws-trainium-neuron-sentinel",
                    "to_member": "quality-gate",
                    "required_inputs": ["NEURON_EXECUTION_GRAPH.json"],
                    "accepted_outputs": ["HARDWARE_INFERENCE_BENCHMARK.md"],
                    "failure_owner": "neuron-engineer"
                }
            ],
            "evidence_requirements": [
                "Empirical latency profiling measurements (TTFT, tokens/sec).",
                "VRAM and memory allocation telemetry receipts.",
                "Perplexity verification benchmarks confirming zero loss of fidelity."
            ],
            "risk_boundaries": [
                "Zero out-of-memory kernel crashes under maximum concurrency.",
                "Strict thermal and compute budget adherence on local Apple Silicon."
            ],
            "quality_gates": [
                "TTFT meets target SLA (<50ms).",
                "Zero memory leaks across 10,000 token execution loops."
            ],
            "state_updates": [
                "Record hardware benchmark in hardware telemetry ledger.",
                "Publish optimal quantization profiles to estate configuration."
            ]
        },
        "compounding": {
            "inherits": [
                "apple-ane-kv-quantizer quantization algorithms",
                "deepseek-mla-moe-sentinel latent attention models",
                "openai-reasoning-kv-sentinel memory budgeting",
                "aws-trainium-neuron-sentinel compiler pipelines",
                "quality-gate benchmark verification"
            ],
            "adds": "Heterogeneous hardware inference orchestration: synthesizes ANE quantization, MoE attention routing, and Trainium execution into an empirically benchmarked inference profile.",
            "compound_artifact": "HARDWARE_INFERENCE_BENCHMARK.md",
            "next_layer_ready_when": [
                "Hardware inference benchmark achieves target throughput.",
                "Quality gate certifies zero OOM or accuracy regression."
            ]
        }
    },
    {
        "id": "forensic-docket-intelligence",
        "display_name": "Forensic Docket Intelligence",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "combo-skills/forensic-docket-intelligence",
        "entrypoint": "combo-skills/forensic-docket-intelligence/COMBO.md",
        "selection": {
            "use_when": [
                "Analyzing court dockets, judicial minute orders, hearing audio recordings, and Bates exhibits to expose perjury or fraud upon the court.",
                "Building comprehensive legal impeachment dossiers with cryptographic evidence cross-referencing."
            ],
            "do_not_use_when": [
                "Informal legal research or general case summaries.",
                "Non-judicial document reviews."
            ]
        },
        "members": [
            {"id": "legal-powerhouse", "kind": "skill", "role": "Structure court case matter, pleading taxonomy, and procedural rules.", "required": True},
            {"id": "audio-forensic-core", "kind": "skill", "role": "Perform WhisperX phonetic alignment, speaker diarization, and ENF validation.", "required": True},
            {"id": "forensic-evidence-chain-core", "kind": "skill", "role": "Verify SHA-256 digests, construct timelines, and stamp Bates exhibits.", "required": True},
            {"id": "epistemic-gate", "kind": "skill", "role": "Enforce L0-L6 epistemic standards on all legal assertions and claims.", "required": True},
            {"id": "quality-gate", "kind": "skill", "role": "Certify evidentiary integrity, FRE 902(13)/(14) compliance, and impeachment proof.", "required": True}
        ],
        "execution": {
            "ordered_steps": [
                {
                    "step": 1,
                    "member_id": "legal-powerhouse",
                    "consumes": ["Court case docket number", "Matter filing history"],
                    "produces": ["CASE_DOCKET_INDEX.json", "Pleading claim matrix"],
                    "validation": "All docket entries and court orders indexed with filing timestamps."
                },
                {
                    "step": 2,
                    "member_id": "audio-forensic-core",
                    "consumes": ["CASE_DOCKET_INDEX.json", "Hearing audio recordings"],
                    "produces": ["AUTHENTICATED_TRANSCRIPT.md", "ENF frequency stability log"],
                    "validation": "Audio transcription achieves 100% phonetic alignment with zero tampering."
                },
                {
                    "step": 3,
                    "member_id": "forensic-evidence-chain-core",
                    "consumes": ["AUTHENTICATED_TRANSCRIPT.md", "Electronic exhibits"],
                    "produces": ["00_FORENSIC_MASTER_TIMELINE.json", "Bates manifest"],
                    "validation": "Deterministic SHA-256 digests generated and Bates serials stamped."
                },
                {
                    "step": 4,
                    "member_id": "epistemic-gate",
                    "consumes": ["00_FORENSIC_MASTER_TIMELINE.json", "Pleading claim matrix"],
                    "produces": ["EPISTEMIC_PROOF_LEDGER.json", "Verified contradiction locks"],
                    "validation": "All claims verified >= L2 behavioral / cryptographic truth level."
                },
                {
                    "step": 5,
                    "member_id": "quality-gate",
                    "consumes": ["EPISTEMIC_PROOF_LEDGER.json", "Bates manifest"],
                    "produces": ["FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md", "Evidentiary signoff"],
                    "validation": "Dossier contains zero ungrounded assertions and satisfies FRE 902 standards."
                }
            ]
        },
        "integration": {
            "handoffs": [
                {
                    "from_member": "legal-powerhouse",
                    "to_member": "audio-forensic-core",
                    "required_inputs": ["CASE_DOCKET_INDEX.json"],
                    "accepted_outputs": ["AUTHENTICATED_TRANSCRIPT.md"],
                    "failure_owner": "legal-analyst"
                },
                {
                    "from_member": "audio-forensic-core",
                    "to_member": "forensic-evidence-chain-core",
                    "required_inputs": ["AUTHENTICATED_TRANSCRIPT.md"],
                    "accepted_outputs": ["00_FORENSIC_MASTER_TIMELINE.json"],
                    "failure_owner": "audio-forensic-specialist"
                },
                {
                    "from_member": "forensic-evidence-chain-core",
                    "to_member": "epistemic-gate",
                    "required_inputs": ["00_FORENSIC_MASTER_TIMELINE.json"],
                    "accepted_outputs": ["EPISTEMIC_PROOF_LEDGER.json"],
                    "failure_owner": "forensic-engineer"
                },
                {
                    "from_member": "epistemic-gate",
                    "to_member": "quality-gate",
                    "required_inputs": ["EPISTEMIC_PROOF_LEDGER.json"],
                    "accepted_outputs": ["FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md"],
                    "failure_owner": "epistemic-auditor"
                }
            ],
            "evidence_requirements": [
                "Cryptographic SHA-256 digests for all exhibits.",
                "Phonetic alignment timestamps with microsecond precision.",
                "Mathematical contradiction proof (e.g. 39-second timestamp impossibility)."
            ],
            "risk_boundaries": [
                "Zero alteration of original audio or document exhibits.",
                "Strict PII scrubbing before any external model exposure."
            ],
            "quality_gates": [
                "All evidentiary assertions backed by Bates citations.",
                "FRE 902(13)/(14) self-authenticating affidavits completed."
            ],
            "state_updates": [
                "Record master timeline in durable evidence register.",
                "Publish intelligence dossier to legal warfare portal."
            ]
        },
        "compounding": {
            "inherits": [
                "legal-powerhouse procedural frameworks",
                "audio-forensic-core acoustic forensics",
                "forensic-evidence-chain-core Bates numbering and hashing",
                "epistemic-gate proof verification",
                "quality-gate evidentiary standards"
            ],
            "adds": "Comprehensive judicial docket forensics: links court docket timelines directly to phonetically aligned hearing transcripts, cryptographic Bates exhibits, and mathematical contradiction proofs.",
            "compound_artifact": "FORENSIC_DOCKET_INTELLIGENCE_DOSSIER.md",
            "next_layer_ready_when": [
                "Master timeline is locked with 100% cryptographic integrity.",
                "Contradiction proofs and Bates manifests are verified by quality-gate."
            ]
        }
    }
]

# ------------------------------------------------------------------------------
# 2. NEW HIGH-BENEFIT MEGA SKILLS DEFINITIONS
# ------------------------------------------------------------------------------
NEW_MEGAS = [
    {
        "id": "apex-autonomous-agent-foundry",
        "display_name": "APEX Autonomous Agent Foundry",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "mega-skills/apex-autonomous-agent-foundry",
        "entrypoint": "mega-skills/apex-autonomous-agent-foundry/MEGA.md",
        "required_combos": [
            "long-horizon-core",
            "autonomous-agent-foundry"
        ],
        "conditional_combos": [
            "capability-readiness",
            "skill-forge",
            "automation-control",
            "guarded-automation-loop"
        ],
        "mission_output": "AGENT_FOUNDRY_MISSION_RESULT.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md"
        ],
        "adds": "End-to-end agent manufacturing mission control: orchestrates multi-agent system architecture, persistent memory topology, statistical evaluation pipelines, and release certification across long-horizon development sprints."
    },
    {
        "id": "apex-architectural-evolution-engine",
        "display_name": "APEX Architectural Evolution Engine",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "mega-skills/apex-architectural-evolution-engine",
        "entrypoint": "mega-skills/apex-architectural-evolution-engine/MEGA.md",
        "required_combos": [
            "long-horizon-core",
            "architectural-refactoring-engine"
        ],
        "conditional_combos": [
            "capability-readiness",
            "closed-loop-code-repair",
            "upstream-fork-harmonization",
            "recon-and-map"
        ],
        "mission_output": "ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md"
        ],
        "adds": "Continuous autonomous codebase modernization: diagnoses architectural bottlenecks, designs formal Architecture Decision Records, conducts clean refactoring with AST self-healing, and enforces Google Senior Staff engineering invariants across the estate."
    },
    {
        "id": "apex-secure-cloud-foundry",
        "display_name": "APEX Secure Cloud Foundry",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "mega-skills/apex-secure-cloud-foundry",
        "entrypoint": "mega-skills/apex-secure-cloud-foundry/MEGA.md",
        "required_combos": [
            "long-horizon-core",
            "secure-service-deployment"
        ],
        "conditional_combos": [
            "capability-readiness",
            "pipeline-orchestration",
            "runtime-operations",
            "automation-control"
        ],
        "mission_output": "SECURE_CLOUD_MISSION_RESULT.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md"
        ],
        "adds": "Long-horizon cloud microservice lifecycle engineering: unifies typed API integration, multi-stage Docker containerization, OWASP security auditing, and MCP gateway registration into verified, production-ready deployments."
    },
    {
        "id": "apex-accelerated-compute-mesh",
        "display_name": "APEX Accelerated Compute Mesh",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "mega-skills/apex-accelerated-compute-mesh",
        "entrypoint": "mega-skills/apex-accelerated-compute-mesh/MEGA.md",
        "required_combos": [
            "long-horizon-core",
            "hardware-accelerated-inference"
        ],
        "conditional_combos": [
            "capability-readiness",
            "polyglot-systems-verification",
            "automation-control"
        ],
        "mission_output": "ACCELERATED_COMPUTE_MISSION_RESULT.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md"
        ],
        "adds": "Hardware-accelerated machine learning control plane: coordinates neural network quantization on Apple Neural Engine, latent attention routing on DeepSeek MoE, and compiler graph execution across AWS Trainium and xAI Colossus superclusters."
    },
    {
        "id": "apex-forensic-litigation-sentinel",
        "display_name": "APEX Forensic Litigation Sentinel",
        "ownership": "glaciereq",
        "maturity": "active",
        "version": "1.0.0",
        "path": "mega-skills/apex-forensic-litigation-sentinel",
        "entrypoint": "mega-skills/apex-forensic-litigation-sentinel/MEGA.md",
        "required_combos": [
            "long-horizon-core",
            "forensic-docket-intelligence"
        ],
        "conditional_combos": [
            "capability-readiness",
            "court-evidence-compiler",
            "voice-evidence-authenticator",
            "automation-control"
        ],
        "mission_output": "FORENSIC_LITIGATION_SENTINEL_RECORD.md",
        "durable_state": [
            "MISSION.md",
            "ROADMAP.md",
            "CONTEXT.md",
            "EVIDENCE.md",
            "HANDOFF.md"
        ],
        "adds": "Autonomous legal prosecution and investigative warfare: dissects judicial dockets, aligns minute-by-minute transcripts against official records, detects 39-second impossibilities, and outputs verified impeachment traps for state and federal courts."
    }
]

# ------------------------------------------------------------------------------
# 3. DISK WRITERS & REGISTRY UPDATERS
# ------------------------------------------------------------------------------
def generate_combo_md(combo: dict) -> str:
    lines = [
        "---",
        f"id: {combo['id']}",
        f"display_name: {combo['display_name']}",
        "schema: ../../schemas/combo-skill.schema.json",
        f"version: {combo['version']}",
        f"status: {combo['maturity']}",
        "---",
        "",
        f"# {combo['display_name']}",
        "",
        "## Purpose and selection",
        "",
        combo["selection"]["use_when"][0],
        f"Do **not** use when {combo['selection']['do_not_use_when'][0].lower()}",
        "",
        "## Incremental value",
        "",
        combo["compounding"]["adds"],
        "",
        "## Member contract",
        "",
        "| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |",
        "|---:|---|---|---|---|---|---|---|"
    ]
    for idx, m in enumerate(combo["members"], 1):
        step = next((s for s in combo["execution"]["ordered_steps"] if s["member_id"] == m["id"]), None)
        consumes = ", ".join(step["consumes"]) if step else "Task inputs"
        produces = ", ".join(step["produces"]) if step else "Artifact outputs"
        val = step["validation"] if step else "Verifies contract"
        lines.append(f"| {idx} | `{m['id']}` | {m['kind'].title()} | {'Yes' if m['required'] else 'No'} | {m['role']} | {consumes} | {produces} | {val} |")

    lines.extend([
        "",
        "## Ordered execution",
        ""
    ])
    for s in combo["execution"]["ordered_steps"]:
        lines.append(f"{s['step']}. **Step {s['step']} — `{s['member_id']}`**: Consumes {', '.join(s['consumes'])}, produces {', '.join(s['produces'])}, and satisfies: {s['validation']}")

    lines.extend([
        "",
        "## Handoff contracts",
        "",
        "| From | To | Required inputs | Accepted output | Failure owner |",
        "|---|---|---|---|---|"
    ])
    for h in combo["integration"]["handoffs"]:
        lines.append(f"| `{h['from_member']}` | `{h['to_member']}` | {', '.join(h['required_inputs'])} | {', '.join(h['accepted_outputs'])} | {h['failure_owner']} |")

    lines.extend([
        "",
        "## Evidence, risks, and state",
        "",
        "The Combo records evidence in its evidence register:",
        "\n".join(f"- {e}" for e in combo["integration"]["evidence_requirements"]),
        "",
        "Risk boundaries:",
        "\n".join(f"- {r}" for r in combo["integration"]["risk_boundaries"]),
        "",
        "## Quality gates",
        "",
        "\n".join(f"- {q}" for q in combo["integration"]["quality_gates"]),
        "",
        "## Compound output",
        "",
        f"**Artifact:** `{combo['compounding']['compound_artifact']}`",
        "",
        "**Ready for Mega Skill integration when:**",
        "",
        "\n".join(f"{idx}. {cond}" for idx, cond in enumerate(combo["compounding"]["next_layer_ready_when"], 1)),
        ""
    ])
    return "\n".join(lines)


def generate_mega_md(mega: dict) -> str:
    lines = [
        f"# {mega['display_name']}",
        "",
        "## Mission",
        "",
        mega["adds"],
        "",
        "## Compounding structure",
        "",
        "| Mandatory route | Conditional route | What the Mega layer adds |",
        "|---|---|---|"
    ]
    for r in mega["required_combos"]:
        if r != "long-horizon-core":
            lines.append(f"| `{r}` | `capability-readiness` | Coordinates end-to-end execution of {r} with mission-level state gates. |")
    for c in mega["conditional_combos"]:
        if c != "capability-readiness":
            lines.append(f"| `long-horizon-core` | `{c}` | Dynamically activates {c} based on mission requirements. |")

    lines.extend([
        "",
        "## Route algorithm",
        "",
        "1. Initialize mission state with `long-horizon-core` and load mission boundary parameters.",
        "2. Evaluate `capability-readiness` for all required and conditional combo routes.",
        f"3. Execute primary pipeline via `{mega['required_combos'][1] if len(mega['required_combos']) > 1 else mega['required_combos'][0]}`.",
        "4. Conditionally dispatch specialist combos based on runtime risk flags and telemetry.",
        f"5. Compile final verified deliverable into `{mega['mission_output']}` and persist immutable state.",
        "",
        "## Durable state",
        "",
        f"`{', '.join(mega['durable_state'])}` maintain durable mission state across sprints and server restarts.",
        ""
    ])
    return "\n".join(lines)


def main():
    # 1. Update combo-skills.json
    combos_data = json.loads(COMBOS_JSON.read_text())
    existing_combo_ids = {e["id"] for e in combos_data["entries"]}
    for c in NEW_COMBOS:
        if c["id"] not in existing_combo_ids:
            combos_data["entries"].append(c)
            existing_combo_ids.add(c["id"])
            print(f"Added Combo Skill to registry: {c['id']}")

        # Write COMBO.md
        c_dir = COMBOS_DIR / c["id"]
        c_dir.mkdir(parents=True, exist_ok=True)
        combo_md = c_dir / "COMBO.md"
        combo_md.write_text(generate_combo_md(c), encoding="utf-8")
        print(f"  Wrote {combo_md}")

    COMBOS_JSON.write_text(json.dumps(combos_data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {COMBOS_JSON} with total {len(combos_data['entries'])} Combo Skills.")

    # 2. Update mega-skills.json
    megas_data = json.loads(MEGAS_JSON.read_text())
    existing_mega_ids = {e["id"] for e in megas_data["entries"]}
    for m in NEW_MEGAS:
        if m["id"] not in existing_mega_ids:
            megas_data["entries"].append(m)
            existing_mega_ids.add(m["id"])
            print(f"Added Mega Skill to registry: {m['id']}")

        # Write MEGA.md
        m_dir = MEGAS_DIR / m["id"]
        m_dir.mkdir(parents=True, exist_ok=True)
        mega_md = m_dir / "MEGA.md"
        mega_md.write_text(generate_mega_md(m), encoding="utf-8")
        print(f"  Wrote {mega_md}")

    MEGAS_JSON.write_text(json.dumps(megas_data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {MEGAS_JSON} with total {len(megas_data['entries'])} Mega Skills.")


if __name__ == "__main__":
    main()
