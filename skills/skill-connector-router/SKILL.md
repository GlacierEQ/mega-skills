---
name: skill-connector-router
description: Mission-preserving skill and connector router. Recovers the entire Operator outcome and verified cursor, composes the strongest coherent set of relevant skills and live connectors, executes reachable authorized branches, verifies results and preserves continuation. Supports efficient loading without capability ceilings and handles skill lifecycle create merge retire promote under Operator authority. Use for skill routing, connector routing, mission composition, dynamic skill selection, execution routing, skill creation and skill lifecycle work.
---

# Skill + Connector Router

**Source owner:** GlacierEQ/computer-user  
**Mirrored in:** GlacierEQ/mega-skills  
**Role:** Mission-preserving front door — recover, compose, dispatch, verify, continue and manage skill lifecycle without blindly loading irrelevant assets.

## Authority boundaries

- This skill owns fast selection, dispatch, and lifecycle proposals/executions under gates.
- `glaciereq-nervous-system` owns full estate composition and cross-session continuation.
- `apex-meta-skill-kernel` owns deep topology, drift, and overlap analysis.
- `prompt-optimizer` owns prompt/skill text improvement.
- Never invent a parallel control plane. Land all new skills in this monolith under `skills/`.

## Default policy (maximum coherent capability, efficient execution)

- No fixed maximum on active specialists. Compose every complementary capability needed for the complete Operator mission; prioritize loading by materiality, dependencies and proven contribution, not an arbitrary count.
- Optimize token and tool cost by using reusable verified context, selective loading and concise status/paths/IDs; do not omit consequential context, capability or evidence to obtain a lighter run.
- Prefer REUSE over CREATE; do not reproduce existing assets or start over from an older cursor.
- Invoke nervous-system whenever estate-wide, multi-repo, cross-session, or complementary-specialist composition materially improves mission execution; this is not an exceptional escalation gate.
- Activate domain skills according to all applicable mission needs, including independent branches. Narrow diagnostic probes remain subordinate to the full mission.

## Verbs

### 1. ROUTE (default)

1. Recover original Operator authority and the current verified execution cursor; map the full mission and its dependent and independent fronts. Use as many mission tags as the actual scope warrants (examples — legal-motion, memory-sync, mcp-health, code-change, evidence, audio, graph, boot).
2. Read `00_CONTROL_PLANE/SKILLS_REGISTRY.md` and list `skills/` (names + descriptions only).
3. Discover connected tools for every consequential mission domain and dependency; account for cross-domain routes, prior verified capabilities and alternate providers.
4. Score skills and connectors for verified functional contribution, complementarity, authority, coverage, dependencies and resilience. Select the strongest coherent mission-bearing set; exclude only demonstrably irrelevant or redundant loads, without deleting or retiring their underlying assets.
5. Dispatch the composed capabilities across currently reachable authorized branches, verify provider-native or test evidence, and continue after any local block. State material omissions and reasons without turning loading choices into mission ceilings.
6. Return source-bound executed results, verification receipts, remaining branches and exact next action. A plan-only result is partial whenever an authorized executable frontier remains.

### 2. CREATE

When a real gap remains after ROUTE scoring:

1. Confirm no existing skill covers the gap (registry + description match).
2. Draft a skill-creator-compliant SKILL.md — kebab-case name matching directory, plain description with triggers, no banned YAML patterns, imperative body, prefer under 500 lines.
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
2. ROUTE — map the complete mission and dependencies → score → compose the strongest coherent specialist set and needed connectors; no fixed numeric cap.
3. If gap → CREATE path (or report blocker).
4. If topology debt → propose MERGE/RETIRE (confirm before apply).
5. DISPATCH → EXECUTE every reachable authorized branch through the selected capabilities; follow alternate routes on local blocks.
6. VERIFY — confirm tools ran or exact blocker.
7. ANSWER — actual outcome delta, provider/readback receipts, unresolved mission scope, continuation cursor and exact next task. Do not represent dispatch, plans or narrow tests as mission completion.

## Output contract

```
ROUTE
  tags: [...]
  selected_skills: [...]
  selected_connectors: [...]
  not_loaded: [...]
  lifecycle: none | create:<name> | merge:<a>+<b>→<survivor> | retire:<name>
  next: <exact tool calls or user task>
```

## Integration

- Reads — SKILLS_REGISTRY.md, skills/*/SKILL.md frontmatter, search_connected_tools.
- Writes — new SKILL.md files, registry updates, optional local export under `.grok/skills/`.
- Escalates to — glaciereq-nervous-system, apex-meta-skill-kernel, prompt-optimizer as needed.
- Companion discipline — max-token-saver and distributed-processing rules apply by default.

## Invariants

- Strongest coherent, evidence-qualified capability composition wins; selective loading is an efficiency mechanism, never a mission-scope ceiling.
- Create only for real gaps.
- Merge/retire keep the constellation clean without losing provenance.
- Max power comes from full mission coverage and complementary proven specialists, without loading irrelevant assets or arbitrarily capping depth, branches or specialist count.

**We. Are. Momentum.**
