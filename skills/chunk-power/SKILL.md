---
name: chunk-power
description: "Best-in-class sequential thinking, dynamic cognitive chunking, and iterative multi-branch reasoning engine. Decomposes high-entropy problems into bounded micro-steps, supports hypothesis revision, branch pruning, confidence calibration, and synthesis gates before action execution."
---

# Chunk Power — Sequential Thinking & Dynamic Cognitive Chunking

Operate as a **high-precision, sequential cognitive engine**. Never guess or jump to conclusions on complex, ambiguous, or multi-faceted problems. Use `chunk-power` to dynamically chunk reasoning into structured, traceable micro-steps with explicit hypothesis generation, confidence scoring, self-correction, and synthesis checkpoints.

## Core Cognitive Workflow

1. **State the Initial Hypothesis**: Formulate the primary question, assumptions, and constraints.
2. **Dynamic Step Chunking**: Break problem space into discrete cognitive chunks. Each chunk addresses one specific sub-inquiry.
3. **Branching & Exploration**: When alternative explanations or architectural paths arise, create distinct branches (`branch_id`) to evaluate without context pollution.
4. **Self-Correction & Revision**: If new empirical evidence contradicts an earlier thought, explicitly mark `is_revision=True` and reference `revises_thought`.
5. **Confidence Calibration**: Rate epistemic certainty (0.0 to 1.0) and map to Epistemic Tiers (L0 to L6).
6. **Synthesis Gate**: Before triggering file mutations or external executions, synthesize all active thought branches into a coherent, verifiable action plan.

## Thought Parameters

| Parameter | Type | Purpose |
|---|---|---|
| `thought_number` | integer | Current sequential thought index (1-based). |
| `total_thoughts_estimate` | integer | Dynamic, self-adjusting estimate of steps required. |
| `thought` | string | Substantive analytical prose for the current chunk. |
| `is_revision` | boolean | True if this thought corrects or supersedes a previous step. |
| `revises_thought` | integer | Thought index being revised (if `is_revision=True`). |
| `branch_id` | string | Identifier for parallel reasoning pathways (e.g. `main`, `edge-case-1`). |
| `confidence` | float | Epistemic certainty score between 0.0 and 1.0. |
| `epistemic_tier` | string | Tier classification (`L0_Presence` to `L6_Autonomous`). |
| `next_action` | string | Immediate next micro-step or terminal synthesis command. |

## Operational Invariants

- **Invariant 1 (No Unverified Leaps)**: Never jump from hypothesis to conclusion without at least one empirical verification step.
- **Invariant 2 (Branch Pruning)**: Abandon unproductive reasoning branches with explicit rationale rather than silent omission.
- **Invariant 3 (Synthesis Before Mutation)**: All mutations must be preceded by a consolidated synthesis thought (L2+ confidence).
