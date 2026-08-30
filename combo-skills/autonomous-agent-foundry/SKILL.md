---
name: autonomous-agent-foundry
description: 'Combo Skill: Autonomous Agent Foundry. Reusable capability chain.'
---

# Autonomous Agent Foundry

## Purpose and selection

Designing, equipping, testing, and benchmarking an autonomous AI agent for production.
Do **not** use when simple one-off prompt adjustments without tool use or memory requirements.

## Incremental value

End-to-end agent lifecycle synthesis: unites architecture, persistent memory, and statistical evaluation into a deployable certified agent packet.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `ai-agents-architect` | Skill | Yes | Architect agent role, tool schemas, and decision planning loops. | Agent operational mandate, Tool capability requirements | AGENT_ARCHITECTURE_SPEC.md, Tool integration schemas | Agent roles, capabilities, and tool boundaries are formally specified. |
| 2 | `agent-memory-mcp` | Skill | Yes | Integrate persistent searchable episodic and semantic memory. | AGENT_ARCHITECTURE_SPEC.md, Memory persistence parameters | AGENT_MEMORY_CONFIGURATION.json, Memory retrieval index | Searchable memory endpoints pass read/write latency and recall tests. |
| 3 | `agent-evaluation` | Skill | Yes | Execute statistical benchmarks, behavioral tests, and adversarial probes. | AGENT_ARCHITECTURE_SPEC.md, AGENT_MEMORY_CONFIGURATION.json, Evaluation test suite | AGENT_EVALUATION_REPORT.json, Accuracy & robustness metrics | Agent achieves >95% benchmark pass rate with zero tool-call hallucinations. |
| 4 | `quality-gate` | Skill | Yes | Validate performance thresholds, accuracy, and zero regression bounds. | AGENT_EVALUATION_REPORT.json, Agent deployment bundle | AGENT_FOUNDRY_RELEASE_PACKET.md, Quality gate certification | All gate criteria pass with zero critical regressions or security vulnerabilities. |

## Ordered execution

1. **Step 1 — `ai-agents-architect`**: Consumes Agent operational mandate, Tool capability requirements, produces AGENT_ARCHITECTURE_SPEC.md, Tool integration schemas, and satisfies: Agent roles, capabilities, and tool boundaries are formally specified.
2. **Step 2 — `agent-memory-mcp`**: Consumes AGENT_ARCHITECTURE_SPEC.md, Memory persistence parameters, produces AGENT_MEMORY_CONFIGURATION.json, Memory retrieval index, and satisfies: Searchable memory endpoints pass read/write latency and recall tests.
3. **Step 3 — `agent-evaluation`**: Consumes AGENT_ARCHITECTURE_SPEC.md, AGENT_MEMORY_CONFIGURATION.json, Evaluation test suite, produces AGENT_EVALUATION_REPORT.json, Accuracy & robustness metrics, and satisfies: Agent achieves >95% benchmark pass rate with zero tool-call hallucinations.
4. **Step 4 — `quality-gate`**: Consumes AGENT_EVALUATION_REPORT.json, Agent deployment bundle, produces AGENT_FOUNDRY_RELEASE_PACKET.md, Quality gate certification, and satisfies: All gate criteria pass with zero critical regressions or security vulnerabilities.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `ai-agents-architect` | `agent-memory-mcp` | AGENT_ARCHITECTURE_SPEC.md | AGENT_MEMORY_CONFIGURATION.json | agent-architect |
| `agent-memory-mcp` | `agent-evaluation` | AGENT_MEMORY_CONFIGURATION.json | AGENT_EVALUATION_REPORT.json | memory-specialist |
| `agent-evaluation` | `quality-gate` | AGENT_EVALUATION_REPORT.json | AGENT_FOUNDRY_RELEASE_PACKET.md | eval-engineer |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Deterministic evaluation logs with confidence intervals.
- Verified memory retrieval latency (<15ms) and recall accuracy (>92%).
- Tool-call parameter validation receipts.

Risk boundaries:
- Zero unvetted system command execution.
- Zero persistent credential exposure in memory graphs.

## Quality gates

- Agent evaluation benchmark score >= 95%.
- All memory write/read assertions pass unit testing.

## Compound output

**Artifact:** `AGENT_FOUNDRY_RELEASE_PACKET.md`

**Ready for Mega Skill integration when:**

1. The agent bundle is certified by quality-gate.
2. Memory retrieval and evaluation reports are attached.
