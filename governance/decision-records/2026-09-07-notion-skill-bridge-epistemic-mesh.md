# 2026-09-07 — Notion skill bridge: epistemic contract, skill mesh, and tool bindings

**Status:** PROPOSED — approval-gated PR on branch `notion-bridge/epistemic-mesh-20260907`; unmerged until the operator approves.

**Owner:** operator (GlacierEQ). Executing agent: Notion AI session, operator-directed, in the current thread.

**Review trigger:** any change to the L0–L6 tiers in `skills/epistemic-gate`, the authority stack in `skills/casey-operator-execution-kernel`, the evidence-state list in `integrations/genius-mastery-bridge.json`, or the Notion page ids / blob SHAs in `integrations/notion-skill-bridge.json`; or the merge itself (re-baseline the manifest).

**Provenance note:** the first copy of this record (commit `836cca0e`, blob `5fed6d0b`) was truncated mid-sentence by a tool-call size limit during the push. This version supersedes it in full. The truncation was detected by readback and is logged in the Notion Ledger (ENTRY 033) as a contradiction that was repaired, not hidden.

## Context

- On 2026-09-07 the operator activated `token-saver`, `max-token-saver`, and the always-on layer (`apex-always-on-core` + `long-horizon-core`) as declarative operating defaults, mirrored the substrate into Notion as AI skill pages, and then directed: enrich, expand, compound and maximize every skill in Notion AND GitHub, with an epistemology focus and explicit connections and tools.
- The repository already carried four overlapping truth vocabularies — the kernel's authority stack, the genius-mastery evidence states, the epistemic-gate L0–L6 tiers, and the holographic-case-mesh proposition record. They are consistent with each other but were never cross-referenced, so "verified" meant something slightly different depending on which file a skill happened to cite.
- There was no machine-readable index tying Notion skill pages to repository skill files. The Notion side referenced repo paths in prose only; drift between the two systems was undetectable.

## Decision

1. Add `docs/EPISTEMIC_CONTRACT.md`: a crosswalk (not a fifth vocabulary) that assigns each existing vocabulary to its owning file, fixes the shared claim types, retrieval states, proof tiers, execution-state ladder, source grades, contradiction law, compaction boundary, and falsification questions, and defines the hook block every skill declares. No new layer, registry entry, or ID is introduced.
2. Add `docs/SKILL_MESH_AND_TOOLS.md`: typed edges between the substrate skills, the Notion legs ↔ repo peers map (by page id), tool bindings per skill, the routing protocol, and the drift check between the two systems.
3. Add `integrations/notion-skill-bridge.json` (genius-mastery-bridge style): Notion page ids ↔ repo paths ↔ blob SHAs at `base_ref`, triggers, typed edges, tool bindings and epistemic hooks per entry; `queued_peers` for repo skills read but not yet hooked; invariants; and a validation recipe. Blob SHAs are the base-ref values and must be re-baselined at merge. Two cosmetic corrections are deferred to that re-baseline: add `provider.first_commit`, and replace `consumer.notion_url_template` with a plain page-id locator (no literal URL stored in the repo).
4. Append a reference-style `## Epistemic contract & Notion bridge — 2026-09-07` hook section to eight files: `skills/max-token-saver/SKILL.md`, `skills/token-saver/SKILL.md`, `mega-skills/apex-always-on-core/MEGA.md`, `combo-skills/long-horizon-core/COMBO.md`, `skills/casey-operator-execution-kernel/SKILL.md`, `skills/power-skill/SKILL.md`, `skills/make-it-heavy/SKILL.md`, `skills/apex-meta-ignition/SKILL.md`. Sections point to the contract, the mesh, and the Notion projection; they do not copy lower-level instructions into MEGA/COMBO files (CONTRIBUTING).
5. Notion mirrors (already live, outside this repo): two new skill pages under the SKILL 5 hub — Epistemic Contract (`f86b7bc950e84c5b9f8b7272883dd18d`) and Skill Mesh & Tool Bindings (`7bcb81c6952d4b83b221a8244da48b34`); eleven existing skill pages enriched with a trigger callout and an "Epistemic hook · Mesh · Tools" section; Legacy Drain flagged as an AI skill. The repo files outrank the Notion projections.

## Alternatives considered

- **New registry layer or new IDs for the contract/mesh** — rejected. HIERARCHY and the registry are the single source of structure; a crosswalk document does not need a layer.
- **Copy Notion page content into the repo** — rejected. `MESH_PEERS.json` route-don't-copy rule; the repo file is canonical and the Notion page is a projection.
- **Fix the README counts while here** — rejected. Out of scope; the registry outranks the README and the lag (709/33/29 vs 714/36/32) is a separate decision.
- **Merge directly** — rejected. The PR is the human control point (the `approve_harmonious_merge_plan` analogue); `pipelines/*.json` are `approval_packet_only` for the same reason.

## Evidence

- Base: `main` @ `0fc5de294d029fddbfdd4d0ee7694203b92981b0` (registry 714 atomic / 36 compound / 32 mega / 7 pipelines / 0 cycles).
- Commit 1 on branch: `836cca0e54bc4012ec0b93bc05fd4470817ebc3b` — `docs/EPISTEMIC_CONTRACT.md` blob `aae71873…` (readback complete), `docs/SKILL_MESH_AND_TOOLS.md` blob `1d077a17…` (readback complete), `integrations/notion-skill-bridge.json` blob `e8de3bf7…` (readback: valid JSON, 18 entries, 12 queued peers, 9 invariants), this record (truncated; superseded here).
- Commit 2+ on branch: this record in full; hook sections on the eight files. Per-file blob SHAs and readback receipts are listed in the PR body.
- Notion receipts: each of the eleven enrichments returned a full-page readback containing the new section; the two new pages appear as children of the SKILL 5 hub on readback.

## Consequences

- Every bridged skill declares the same hook block, so compliance with the contract is uniform and greppable: `rg "Epistemic contract & Notion bridge"`.
- Drift between Notion and repo becomes detectable: page id ↔ path ↔ blob SHA in one file, with a stated drift check.
- At merge, the manifest must be re-baselined (`provider.base_ref`, blob SHAs, `first_commit`, locator field).
- Twelve `queued_peers` (`master`, `holographic-case-mesh`, `epistemic-gate`, `epistemic-verification-chain`, `local-skill`, `notion-sync-automation`, `sequential-thinking`, `forensic-evidence-chain-core`, `apex-casebuild-mesh`, `apex-legal-warfare`, `apex-omniversal-memory`, `apex-orchestrator-mesh`) are indexed but NOT hooked in this PR.

## Safety

- No credentials, private evidence, personal records, or runtime state are added. Notion is referenced by page id only — no URLs.
- Registry, HIERARCHY, OWNERSHIP, IDs, layers and dependencies are unchanged; `scripts/validate_hierarchy.py` is unaffected.
- GitHub Actions is budget-blocked, so CI will likely not run. Operator validation before merge: `jq empty integrations/notion-skill-bridge.json`, `python scripts/validate_hierarchy.py`, `python -m unittest discover -s tests -v`.

## Rollback

- Close the PR or revert the branch; nothing on `main` changes until approval.
- Notion sections remain as historical record with a SUPERSEDES note pointing to this DR if the decision is reversed.
