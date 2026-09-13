---
name: concise-planning
description: "Use when a user asks for a plan for a coding task, to generate a clear, actionable, and atomic checklist."
---

# Concise Planning

## Goal

Turn a user request into a **single, actionable plan** with atomic steps and complete mission coverage.

## Workflow

### 1. Scan Context

- Read `README.md`, docs, and relevant code files.
- Identify constraints (language, frameworks, tests).

### 2. High-Signal Interaction

- Ask questions only when they block correct execution or materially change the mission.
- Make explicit, evidence-backed assumptions for non-blocking unknowns.
- Do not suppress necessary clarification merely to keep the exchange short.

### 3. Generate Plan

Use the following structure:

- **Approach**: 1-3 sentences on what and why.
- **Scope**: Bullet points for "In" and "Out".
- **Action Items**: Enough atomic, ordered tasks to cover the complete request.
- **Validation**: Items for tests, readback, adversarial checks, and approval gates where relevant.

## Plan Template

```markdown
# Plan

<High-level approach>

## Scope

- In:
- Out:

## Action Items

[ ] <Step 1: Discovery>
[ ] <Step 2: Implementation>
[ ] <Step 3: Implementation>
[ ] <Step 4: Validation/Testing>
[ ] <Step 5: Rollout/Commit>

## Open Questions

- <Blocking question, if any>
```

## Checklist Guidelines

- **Atomic**: Each step is a single logical unit of work.
- **Verb-first**: "Add...", "Refactor...", "Verify...".
- **Concrete**: Name specific files or modules when possible.
- **Complete**: Include mission-relevant edge cases, integration, and proof; do not omit them to reduce plan size.
