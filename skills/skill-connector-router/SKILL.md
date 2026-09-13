---
name: skill-connector-router
description: "Dynamic skill and connector router for strong quota-aware runs. Scores intent, composes the strongest relevant skill coalition and live connectors, dispatches them with parallelism where safe, and manages skill lifecycle create merge retire promote so the constellation stays coherent and high-leverage."
---

# Skill + Connector Router

**Repo target:** GlacierEQ/computer-user  
**Role:** Fast-path front door — select, create, merge, retire — without loading irrelevant estate material or starving mission-relevant capability.

## Authority boundaries

- This skill owns fast selection, dispatch, and lifecycle proposals/executions under gates.
- `glaciereq-nervous-system` owns full estate composition and cross-session continuation.
- `apex-meta-skill-kernel` owns deep topology, drift, and overlap analysis.
- `prompt-optimizer` owns prompt/skill text improvement.
- Never invent a parallel control plane. Land all new skills in this monolith under `skills/`.

## Default policy (quota-aware, capability-preserving)

- Compose the strongest relevant specialist coalition that covers the mission, with no arbitrary skill-count ceiling. A larger coalition needs an explicit rationale and collision control.
- Compress redundancy and transport overhead, not mission scope, reasoning, evidence, or implementation strength.
- Prefer REUSE over CREATE when reuse preserves or strengthens the required capability.
- Escalate to nervous-system for estate-wide, multi-repo, cross-session, or high-coordination work.
- Load power-skill / potato-peeler / legal-motion-template and other specialists whenever mission tags or risk require them.
- Dispatch independent specialists in parallel when isolation and authorization permit; keep dependent work ordered.

## Verbs

### 1. ROUTE (default)

1. Parse user intent into mission tags (examples — legal-motion, memory-sync, mcp-health, code-change, evidence, audio, graph, boot).
2. Read `00_CONTROL_PLANE/SKILLS_REGISTRY.md` and list `skills/` (names + descriptions only).
3. Call `search_connected_tools` for every domain implied by the tags and material risk.
4. Score skills and connectors for relevance, complementarity, evidence coverage, and execution value. Select the strongest justified coalition with complete coverage; deduplicate only genuinely redundant roles.
5. Dispatch selected specialists, using safe parallelism for independent work. State what was not loaded and why.
6. Return a high-signal plan — selected skills, selected connectors, exact next tool calls, do-not-load list, and coverage rationale.

### 2. CREATE

When a real gap remains after ROUTE scoring:

1. Confirm no existing skill covers the gap (registry + description match).
2. Draft a skill-creator-compliant SKILL.md — kebab-case name matching directory, plain description with triggers, no banned YAML patterns, imperative body, sized for complete capability.
3. Land under `skills/<name>/SKILL.md` in GlacierEQ/computer-user.
4. Append a row to `00_CONTROL_PLANE/SKILLS_REGISTRY.md`.
5. Optionally export to `/home/workdir/.grok/skills/<name>/` for local use.
6. Do not create scripts/references/assets unless the skill needs deterministic code or long docs.

### 3. MERGE

When overlap or duplication is detected (or meta-kernel recommends MERGE):

1. Identify survivor skill and absorb targets.
2. Consolidate unique instructions into the survivor; preserve provenance notes.
3. Update registry — mark absorbed skills RETIRED with pointer to survivor.
4. Do not silently delete files; retire in place or move to an archive path if one exists.
5. Require explicit user confirmation for destructive merges unless pre-authorized for that session.

### 4. RETIRE

When a skill is unused, stale, redundant, or superseded:

1. Mark RETIRED in SKILLS_REGISTRY with reason and replacement if any.
2. Keep SKILL.md readable as historical reference unless user authorizes removal.
3. Never retire nervous-system, meta-skill-kernel, or this router without explicit override.

### 5. PROMOTE

When a host projection should become canonical or a local skill should land in the monolith:

1. Validate frontmatter and structure.
2. Push to GlacierEQ/computer-user `skills/` and update registry.
3. Record source and commit when promoting from another repo.

## Process for every turn that invokes this skill

1. OBJECTIVE LOCK — one sentence restatement of the goal.
2. ROUTE — tags → score → compose the strongest relevant coalition + needed connectors.
3. If gap → CREATE path (or report blocker).
4. If topology debt → propose MERGE/RETIRE (confirm before apply).
5. DISPATCH the coalition with safe parallelism and explicit ownership.
6. VERIFY — confirm tools ran or exact blocker.
7. ANSWER — high-signal status, artifact paths, coverage, and next exact task.

## Output contract

```
ROUTE
  tags: [...]
  selected_skills: [...]
  selected_connectors: [...]
  coverage: [...]
  not_loaded: [...]
  lifecycle: none | create:<name> | merge:<a>+<b>→<survivor> | retire:<name>
  next: <exact tool calls or user task>
```

## Integration

- Reads — SKILLS_REGISTRY.md, skills/*/SKILL.md frontmatter, search_connected_tools.
- Writes — new SKILL.md files, registry updates, optional local export under `.grok/skills/`.
- Escalates to — glaciereq-nervous-system, apex-meta-skill-kernel, prompt-optimizer as needed.
- Companion discipline — max-token-saver and distributed-processing rules apply by default, with capability preservation.

## Invariants

- The strongest relevant coalition wins; irrelevant loading is still avoided.
- Create only for real gaps.
- Merge/retire keep the constellation coherent without losing provenance or unique capability.
- Quota awareness governs transport and redundancy, never the mission's justified capability ceiling.

**We. Are. Momentum.**
