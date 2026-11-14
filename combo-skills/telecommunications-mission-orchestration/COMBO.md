---
id: telecommunications-mission-orchestration
display_name: Telecommunications Mission Orchestration
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: candidate
---

# Telecommunications Mission Orchestration

## Purpose and selection
Use when an APEX mission must plan, execute, interpret, verify, and preserve a voice/SMS/SIP/PSTN/WebRTC communication without confusing transport success with mission success.

Do not use for casual audio transcription with no communication mission; use the existing voice/transcription skills directly.

## Incremental value
This Compound Skill binds realtime voice engineering, telecom mission semantics, provider-native receipts, forensic provenance, and quality gates into one reusable communication-execution contract. Child methods remain canonical in their own Skills.

## Member contract
| Order | Member ID | Kind | Required | Role |
|---:|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Bound objective, authority, target, evidence and stop conditions. |
| 2 | `telecommunications-execution-core` | Skill | Yes | Preflight, state normalization, receipt verification and false-success prevention. |
| 3 | `voice-ai-development` | Skill | No | Realtime provider/latency architecture for voice routes. |
| 4 | `voice-agents` | Skill | No | Conversational turn-taking, interruption and voice-agent behavior. |
| 5 | `whisperx-audio-processing` | Skill | No | High-assurance post-call transcription when source audio exists. |
| 6 | `voice-evidence-authenticator` | Compound Skill | No | Evidentiary authentication when a recording becomes material evidence. |
| 7 | `forensic-evidence-chain-core` | Skill | Yes | Preserve originals, hashes, derivative lineage and provider provenance. |
| 8 | `agent-evaluation` | Skill | No | Scenario/eval scoring for agent behavior and reliability. |
| 9 | `quality-gate` | Skill | Yes | Promotion gate before mission state advances. |

## Ordered execution
1. `mission-contract` emits the bounded mission packet and approval boundary.
2. `telecommunications-execution-core` fails closed on stale context, missing authority, invalid destination or unsupported semantics.
3. Voice routes conditionally invoke `voice-ai-development` + `voice-agents`; text routes keep voice skills dormant.
4. Provider adapter executes only under the external runtime's authorization contract and returns native readback.
5. `telecommunications-execution-core` normalizes independent transport/contact/mission/ack state and rejects false success.
6. If audio is material, invoke WhisperX; if evidentiary authentication is required, invoke `voice-evidence-authenticator` without altering originals.
7. `forensic-evidence-chain-core` binds receipt/transcript/recording hashes and lineage.
8. `quality-gate` accepts, repairs, or redispatches. Only accepted evidence advances durable mission state.

## Handoff contract
Mission packet → provider plan → native provider receipt → semantic receipt → evidence/provenance packet → APEX/Attio/DOCKETS projections.

## Risk boundaries
- No autonomous external call/SMS authority is granted by this Skill.
- No provider becomes sovereign because it is currently cheapest or easiest.
- No model-generated narration substitutes for provider readback.
- No upstream Pipecat/LiveKit/Fonoster core patch when an adapter/sidecar suffices.

## Compound output
**Artifact:** `TELECOMMUNICATIONS_EXECUTION_RECORD.md` plus machine-readable receipt/provenance objects.

## Ready for Mega integration when
1. preflight and receipt verification are machine-tested;
2. provider-native evidence is retained;
3. false-success tests pass;
4. downstream projections are source-linked, not source-replacing.
