---
id: multi-agent-orchestration-mesh
display_name: Multi-Agent Orchestration Mesh
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Multi-Agent Orchestration Mesh

## Purpose and selection

Multi-agent team coordination, tool building, dynamic routing, and dialectic consensus are required.

## Incremental value

This Combo Skill composes ai-agents-architect, agent-tool-builder, chunk-power into a unified, verified `SWARM_CONSENSUS_RECORD.md`.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `ai-agents-architect` | skill | Yes | Architect multi-agent topology and assign specialist boundaries. | Task mandate, Agent topology spec | agent-mesh-topology.json | Agent roles and supervisor boundaries are strictly defined. |
| 2 | `agent-tool-builder` | skill | Yes | Synthesize dynamic tool schemas and invocation contracts. | agent-mesh-topology.json | tool-manifest.json | Tool schemas conform to strict JSON-schema specs. |
| 3 | `chunk-power` | skill | Yes | Execute sequential thinking, branch exploration, and synthesis gates. | tool-manifest.json | SWARM_CONSENSUS_RECORD.md | Synthesis gate verifies 100% alignment across agents. |

## Ordered execution

1. **ai-agents-architect** consumes Task mandate, Agent topology spec, produces agent-mesh-topology.json, and verifies Agent roles and supervisor boundaries are strictly defined..
2. **agent-tool-builder** consumes agent-mesh-topology.json, produces tool-manifest.json, and verifies Tool schemas conform to strict JSON-schema specs..
3. **chunk-power** consumes tool-manifest.json, produces SWARM_CONSENSUS_RECORD.md, and verifies Synthesis gate verifies 100% alignment across agents..

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `ai-agents-architect` | `agent-tool-builder` | agent-mesh-topology.json | tool-manifest.json | `ai-agents-architect` | Verified handoff |
| `agent-tool-builder` | `chunk-power` | tool-manifest.json | SWARM_CONSENSUS_RECORD.md | `agent-tool-builder` | Verified handoff |

## Compound output

Produce `SWARM_CONSENSUS_RECORD.md` upon completion.
