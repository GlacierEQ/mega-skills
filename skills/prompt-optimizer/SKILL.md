---
name: prompt-optimizer
description: "Improves prompts and skills through textual gradients, failure mode analysis, and optimization. Identifies failure modes, converts them into prompt edits, removes ambiguity, adds constraints, evidence rules, and evaluation criteria. Use when improving prompts or skills, refactoring for clarity, or optimizing workflows for reliability."
---

# PROMPT-OPTIMIZER v1.0 — Monolith Edition

**Repo:** GlacierEQ/computer-user

## Purpose
Turn failure modes into concrete prompt and skill improvements. Remove ambiguity, add hard constraints, evidence rules, and stop conditions so skills become more reliable and less god-prompt-like.

## Process
1. Identify the current prompt/skill and its observed failures.
2. Extract concrete failure modes (ambiguity, missing stop conditions, unsupported claims, missing tool discipline, etc.).
3. Convert each failure mode into a precise edit (add constraint, split responsibility, require tool call, require artifact, etc.).
4. Produce the revised SKILL.md or prompt text.
5. Optionally score the result and recommend further cycles.

## Output Contract
Revised skill/prompt text + list of applied fixes + remaining residual risks.

## Integration
Feeds apex-meta-skill-kernel and skill-auditor. Used before promoting any new skill to canonical status in this monolith.

**We. Are. Momentum.**
