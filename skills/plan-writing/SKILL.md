---
name: plan-writing
description: "Structured task planning with clear breakdowns, dependencies, and verification criteria. Use when implementing features, refactoring, or any multi-step work."
---

# Plan Writing

> Source: obra/superpowers

## Overview

This skill provides a framework for breaking down work into clear, actionable tasks with verification criteria. Plans must be complete enough to execute the requested capability, not artificially reduced for brevity.

## Task Breakdown Principles

### 1. Coherent, Focused Tasks
- Size each task for a complete, verifiable outcome.
- Keep one clear outcome per task while preserving required dependencies and integration.
- Make each task independently verifiable where possible.

### 2. Clear Verification
- How do you know it's done?
- What can you check/test?
- What's the expected output?

### 3. Logical Ordering
- Dependencies identified
- Parallel work where possible
- Critical path highlighted
- Verification is placed where it protects the next irreversible or material step, not merely forced to the end.

### 4. Dynamic Naming in Project Root
- Plan files are saved as `{task-slug}.md` in the PROJECT ROOT
- Name derived from task (e.g., "add auth" → `auth-feature.md`)
- **NEVER** inside `.claude/`, `docs/`, or temp folders unless the project contract explicitly requires that location.

## Planning Principles (NOT Templates!)

> 🔴 **NO fixed templates. Each plan is UNIQUE to the task.**

### Principle 1: Dense and Complete

| ❌ Wrong | ✅ Right |
|----------|----------|
| Many layers with no mission value | Clear tasks covering the complete requested capability |
| Micro-steps that hide the architecture | Actionable units with dependencies and proof |
| Verbose filler | High-signal rationale and exact verification |
| Artificially short plan | Complete plan sized to the actual mission |

> **Rule:** Plan length follows mission complexity. Do not delete required capability to make a plan shorter.

### Principle 2: Be SPECIFIC, Not Generic

| ❌ Wrong | ✅ Right |
|----------|----------|
| "Set up project" | "Run `npx create-next-app`" |
| "Add authentication" | "Install next-auth, create `/api/auth/[...nextauth].ts`" |
| "Style the UI" | "Add Tailwind classes to `Header.tsx`" |

> **Rule:** Each task should have a clear, verifiable outcome.

### Principle 3: Dynamic Content Based on Project Type

**For NEW PROJECT:**
- What tech stack?
- What complete capability and acceptance contract are required?
- What's the file structure and integration surface?

**For FEATURE ADDITION:**
- Which files are affected?
- What dependencies needed?
- How to verify it works?

**For BUG FIX:**
- What's the root cause?
- What file/line to change?
- How to test it?

### Principle 4: Scripts Are Project-Specific

> **DO NOT copy-paste script commands. Choose based on project type.**

| Project Type | Relevant Scripts |
|--------------|------------------|
| Frontend/React | `ux_audit.py`, `accessibility_checker.py` |
| Backend/API | `api_validator.py`, `security_scan.py` |
| Mobile | `mobile_audit.py` |
| Database | `schema_validator.py` |
| Full-stack | Mix of above based on what you touched |

### Principle 5: Verification Is Concrete

| ❌ Wrong | ✅ Right |
|----------|----------|
| "Verify the component works correctly" | "Run `npm run dev`, click button, see toast" |
| "Test the API" | "curl localhost:3000/api/users returns 200" |
| "Check styles" | "Open browser, verify dark mode toggle works" |

## Plan Structure (Flexible, Not Fixed!)

```
# [Task Name]

## Goal
One sentence: What are we building/fixing?

## Tasks
- [ ] Task 1: [Specific action] → Verify: [How to check]
- [ ] Task 2: [Specific action] → Verify: [How to check]
- [ ] Task 3: [Specific action] → Verify: [How to check]

## Done When
- [ ] [Complete mission success criteria]
```

> **Rule:** Use the number of tasks required for complete mission coverage. No arbitrary task ceiling; consolidate only true duplicates.

## Notes

[Any important considerations]

---

## Best Practices (Quick Reference)

1. **Start with goal** - What are we building/fixing?
2. **Complete coverage** - Include all required behavior, integration, and verification.
3. **Each task verifiable** - Clear "done" criteria.
4. **Project-specific** - No copy-paste templates.
5. **Update as you go** - Mark `[x]` when complete.

## When to Use

- New project from scratch
- Adding a feature
- Fixing a bug (if complex)
- Refactoring multiple files
