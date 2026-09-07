# 2026-09-07 — Notion skill bridge: epistemic contract, skill mesh, and tool bindings

**Status:** PROPOSED — approval-gated PR on branch `notion-bridge/epistemic-mesh-20260907`; unmerged until the operator approves.
**Owner:** operator (GlacierEQ). Executing agent: Notion AI session, operator-directed, in the current thread.
**Review trigger:** any change to the L0–L6 tiers in `skills/epistemic-gate`, the authority stack in `skills/casey-operator-execution-kernel`, the evidence-state list in `integrations/genius-mastery-bridge.json`, or the Notion page ids / blob SHAs in `integrations/notion-skill-bridge.json`; or the merge itself (re-baseline the manifest).

## Context

- On 2026-09-07 the operator activated the always-on substrate in Notion (max-token-saver, apex-always-on-core, the operator execution kernel, power-skill, pipelines) as Notion AI skills mirroring this repository at `0fc5de294d029fddbfdd4d0ee7694203b92981b0`, then directed: enrich, expand, compound, and maximize each skill in Notion **and** GitHub, with an epistemology focus; connections and tools are a plus.
- The repository already carries four overlapping truth vocabularies — the kernel's six-layer loop and authority stack, the genius-mastery evidence / outcome states, the epistemic-gate L0–L6 tiers, and the holographic-case-mesh proposition record. They are consistent but were not cross-referenced, so skills could not declare compliance uniformly and "verified" meant different things in different files.
- No machine-readable index existed between Notion skill pages and repository skill files, so Notion ↔ repo drift was undetectable.

## Decision

1. Add `docs/EPISTEMIC_CONTRACT.md`: a crosswalk that names the executable owner of each vocabulary and defines the hook block every skill declares (claims emitted, states it may promote to, receipts, contradiction routing, compaction exceptions). No new layer, no new registry entry.
2. Add `docs/SKILL_MESH_AND_TOOLS.md`: typed edges between substrate skills, Notion-leg ↔ repo-peer mapping, tool bindings per skill, routing protocol, and a read-only drift check.
3. Add `integrations/notion-skill-bridge.json` (genius-mastery-bridge style): Notion page ids ↔ repo paths 