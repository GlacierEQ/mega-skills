---
name: apex-boot-core
description: "Operator-bound holographic estate bootstrap and enrichment sentinel. Binds Operator semantics before interpretation, observes estate state, emits level-up enrichment transitions, and detects authority/ontology inversions without creating machine veto or sovereignty."
---

# APEX Boot Core

## Purpose

APEX Boot Core is a **capability node in the GlacierEQ holographic/polycentric mesh**. It does not acquire project-direction authority, root status, sovereignty, or mission-veto power.

**The Operator alone holds project-direction authority.**

Boot Core binds the Operator semantics contract before interpreting estate state, then observes the estate and converts every result into an **enrichment transition / literal level-up**.

## Prime Semantic Law

```text
OPERATOR AUTHORITY
      ↓
RECOVER OPERATOR SEMANTICS
      ↓
BIND TERMS
      ↓
RECOVER TASK CONTEXT
      ↓
OBSERVE / TEST / ACQUIRE EVIDENCE
      ↓
ENRICH STATE
      ↓
LEVEL UP
      ↓
REPAIR / COMPOSE / REROUTE AS USEFUL
      ↓
VERIFY → PERSIST → CONTINUE
```

A gate is never a mission permission check.

| Telemetry | Enrichment transition |
|---|---|
| `PASS` | `VALIDATED_LEVEL_UP` |
| `WARN` | `ENRICH_WITH_UNCERTAINTY` |
| `FAIL` | `LOCALIZE_REPAIR_REROUTE_LEVEL_UP` |
| `MISSING` | `DISCOVER_ACQUIRE_LEVEL_UP` |
| `DRIFT` | `RECONCILE_ENRICH_LEVEL_UP` |

A local block changes route, not objective. A temporary skip changes sequencing, not scope. Only the Operator changes mission or project direction.

## Holographic Mesh Law

- No repository, model, verifier, provider, runtime, receipt, CI system, projection, or gate becomes the sole machine authority.
- Overlapping systems are evaluated for composition, enrichment, lineage, interoperability, and capability-donor preservation.
- Current route selection is routing metadata, not authority transfer.
- Negative evidence enriches state and creates repair/reroute opportunities; it never becomes a global veto.
- Durable receipts preserve evidence and provenance; receipts do not create authority.

## Pre-Reasoning Binding

The durable semantic contract lives at:

`resources/operator_semantics.json`

The executable projection and ontology-inversion detector live at:

`scripts/operator_semantics.py`

Before interpretation, Boot Core projects:

- Operator authority holder
- holographic/polycentric topology
- enrichment-transition gate semantics
- local-block routing law
- mission-change authority
- semantic-contract digest and binding diagnostics

The detector identifies recurring inversions such as:

- assigning sole/final authority to a machine node;
- interpreting a failed gate as a mission veto;
- converting a local deficiency into a global mission stop;
- collapsing the mesh into a single/canonical machine root.

Detector findings are themselves enrichment telemetry: repair the interpretation and continue.

## Standard Procedure

Run the v2 boot and emit the complete machine-readable receipt:

```bash
python scripts/boot_watchdog.py --json
```

Optionally persist a receipt:

```bash
python scripts/boot_watchdog.py --json --save /path/to/receipt.json
```

Equivalent entrypoints:

```bash
python scripts/run.py --json
python scripts/this_skill.py --json
python skill.py --json
```

All four entrypoints delegate to the same v2 implementation.

## Current Estate Observations

The 12 estate observations currently cover environment/runtime, secrets posture, receipt-chain linkage, Monolith census, APEX-IMPACT availability, personalization-kernel availability, memory-engine availability, token-saver availability, estate-quality receipt state, Git working-tree telemetry, POSIX toolchain executability, and capability-bus discovery.

These observations are **not** permissions to proceed. They increase evidence, surface deficiencies, activate repair/composition/rerouting opportunities, and advance the estate to a richer state.

## Regression Law

Every repeated ontology failure should become a durable regression test. Current tests explicitly reject:

- non-Operator sole-authority assignment;
- gate-as-veto reasoning;
- local-block-as-global-block reasoning;
- collapse to a single machine root;
- legacy `this_skill.py` bypass;
- documentation/runtime CLI drift.

The intended invariant is not "remember the correction later." It is **bind the Operator ontology before reasoning and detect departures before they propagate**.
