---
id: multi-agent-orchestration-mesh
display_name: Multi-Agent Orchestration Mesh
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Multi-Agent Orchestration Mesh

## Purpose and selection

Multi-agent team coordination, tool building, dynamic routing, bounded parallel execution, contradiction preservation, and evidence-weighted synthesis are required.

## Incremental value

This Combo Skill composes ai-agents-architect, agent-tool-builder, and chunk-power into a unified, verified `SWARM_CONSENSUS_RECORD.md` that records converged findings, surviving contradictions, minority reports, provenance, and the next probe needed to resolve unresolved dissent.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `ai-agents-architect` | skill | Yes | Architect multi-agent topology and assign specialist boundaries. | Task mandate, Agent topology spec | agent-mesh-topology.json | Agent roles and supervisor boundaries are strictly defined. |
| 2 | `agent-tool-builder` | skill | Yes | Synthesize dynamic tool schemas and invocation contracts. | agent-mesh-topology.json | tool-manifest.json | Tool schemas conform to strict JSON-schema specs. |
| 3 | `chunk-power` | skill | Yes | Execute branch exploration, parallel challenger lanes, contradiction-preserving synthesis, and evidence-weighted convergence gates. | tool-manifest.json | SWARM_CONSENSUS_RECORD.md | Synthesis gate preserves unresolved dissent and only marks convergence where evidence supports it. |

## Ordered execution

1. **ai-agents-architect** consumes Task mandate, Agent topology spec, produces agent-mesh-topology.json, and verifies Agent roles and supervisor boundaries are strictly defined..
2. **agent-tool-builder** consumes agent-mesh-topology.json, produces tool-manifest.json, and verifies Tool schemas conform to strict JSON-schema specs..
3. **chunk-power** consumes tool-manifest.json, produces SWARM_CONSENSUS_RECORD.md, and verifies unresolved contradictions remain explicit while evidence-supported agreements are promoted.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `ai-agents-architect` | `agent-tool-builder` | agent-mesh-topology.json | tool-manifest.json | `ai-agents-architect` | Verified handoff |
| `agent-tool-builder` | `chunk-power` | tool-manifest.json | SWARM_CONSENSUS_RECORD.md | `agent-tool-builder` | Verified handoff |

## Swarm invariants

- Independent lanes may disagree; disagreement is evidence to preserve, not noise to erase.
- No majority vote, confidence average, or supervisor preference may overwrite stronger source-bearing evidence.
- Unresolved dissent remains explicit with claimant, evidence, counterevidence, confidence, and next probe.
- Fan-out must be bounded by mission budget, dependency topology, and supervisor depth.
- Shark Laser and Gatling Tsunami are routing modes: concentrated depth and distributed saturation may switch dynamically without changing the truth model.
- A worker result is not a mission result until synthesis, verification, and receipt binding complete.

## Compound output

Produce `SWARM_CONSENSUS_RECORD.md` upon completion. The artifact name is retained for compatibility; "consensus" means evidence-supported convergence plus preserved unresolved dissent, never forced agreement.
