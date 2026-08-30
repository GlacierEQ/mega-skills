---
name: monolith
description: Operating inside the Monolith meta-layer at /root/projects/monolith.
  Use when working with the catalog, the integration fabric, mega-skills, or the propagation
  contract. Monolith is upstream of all other projects; updates here propagate via
  the contract, not via direct edits downstream.
version: 0.1.0
---

# Monolith Skill

Meta-layer that owns the catalog, integration fabric, mega-skills, and the
propagation contract. It is **upstream** of every other project in the
workspace and has **no runtime of its own**.

**Do not duplicate APEX doctrine here — load `apex-sovereign-runtime` first.**

## Project Layout

| Path | Purpose |
|------|---------|
| `catalog/` | JSON catalogs: `core_mesh.json`, `mega_skills.json`, `legal_category.json`, `unification_manifest.json`, `growth_ledger.json`, `integration_fabric.json` |
| `foundations/` | Distillation protocol, epistemic methodology, helix-spiral, excellence contract |
| `unification/` | Propagation plan generators |
| `tools/` | `audit_semantic_contracts.py`, `propagate_unification.py`, `propagate_protected_consumers.py`, `build_estate_map.py` |
| `tests/` | 4 test files covering contracts, protected consumers, unification propagation, and estate map |
| `EXCELLENCE.md` | Top-level contract this project enforces on all downstream |

## Entry Points

```bash
# List all known capabilities
cd /root/projects/monolith && python -m monolith.catalog

# Generate the propagation plan for downstream projects
cd /root/projects/monolith && python -m monolith.unification

# Apply the contract to a downstream project
cd /root/projects/monolith && python -m monolith.foundations
```

## Test Command

```bash
cd /root/projects/monolith && python -m pytest tests/ -v
```

## Hard Rules (Non-Negotiable)

1. **Monolith is meta-only.** It does not implement runtime behavior. If you
   need to add a feature, you add a contract entry here and a downstream
   project implements it. Do not import runtime modules from other
   projects into Monolith.
2. **Updates propagate via the contract**, not via direct file edits in
   downstream projects. If you're tempted to "fix" something inside
   another project while in Monolith, stop. Generate the propagation
   plan and let the downstream project pull.
3. **APEX doctrine applies** (`apex-sovereign-runtime`). Identity is
   strict; receipts for every state change; lanes own their domains.
4. **The catalog is the source of truth.** If a capability is not in
   `catalog/`, it does not exist from Monolith's perspective. Don't
   reference a thing that isn't cataloged.
5. **No tool without a test.** 4 test files today; each one maps to a
   tool. New tool → new test in the same commit.

## When to Use This Skill

- Adding a new capability that downstream projects should adopt
- Auditing whether a downstream project is in sync with the catalog
- Generating a propagation plan after a catalog change
- Editing `EXCELLENCE.md` or the `foundations/` documents
- Running `tools/audit_semantic_contracts.py` or
  `tools/build_estate_map.py`

## When NOT to Use This Skill

- Implementing a feature in `make-it-heavy` or `mastermind` — those
  have their own project skills
- Touching tower-of-babel registry/index files — that has its own
  doctrine (`tower-of-babel` skill, this set)
- Pure documentation work — `clean-code` is enough

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Editing a downstream project from inside Monolith | critical | Generate the propagation plan; let downstream pull. |
| Capability referenced but not in `catalog/` | critical | Add to catalog first, then reference. The catalog is the source of truth. |
| Contract change without a corresponding audit-tool update | high | Every catalog/contract change must update the audit tool in the same commit. |
| Tool added without a test | critical | No tool merges without `tests/test_<tool>.py` (rule 5 above). |
| Forgetting to run the propagation after editing `core_mesh.json` | high | `python -m monolith.unification` after every catalog change. |
| Importing downstream runtime modules | critical | Monolith is meta-only. Reference by name + contract, not by import. |

## Related Skills

- `apex-sovereign-runtime` — APEX doctrine (load first)
- `mastermind` — one of the downstream projects Monolith governs
- `make-it-heavy` — another downstream
- `tower-of-babel` — independent of Monolith, has its own doctrine
- `clean-code` — pragmatic style for Monolith's own Python
