# Worked Example — Unified Boot Chain Mission

A real mission executed under the Progressive Pyramid Protocol, with
source-native receipts. Mission: tie the estate's two boot halves
(aspen-grove-core and apex-boot-core) into one verified chain.

## Mission initialization

- Original intent: one fail-closed boot path with proof, not prose
- Acceptance criteria: both heads reference one contract; every stage gated on
  exit code + fresh receipt + parsed status; chain receipt binds stage receipts
- Protected capabilities: vault bootstrap, memory mesh boot, 12-gate audit
- Authoritative sources: BOOTUP_PROTOCOL.md, hydration.contract.json,
  APEX_UNIFIED_BOOT.py, universal_memory_boot.py

## Corner 1 — CONTEXT -> V1

Recovered estate state: 884 repos surveyed, boot surfaces located, code read.
V1: analysis identifying aspen-grove-core as boot head and the existing
handoff seam (probe_memory_mesh reading the Aspen receipt via ASPEN_GROVE_CORE).
Receipt: estate analysis canvas, 2026-10-12.

## Corner 2 — OBJECTIVE -> V2

Inherited V1. Objective sharpened: not "pick the strongest bootup" but "make
the two-half handshake executable and mandatory." V2: four-stage chain design
(INGRESS, HYDRATE, ACTIVATE, PERSIST) with fail-closed gates.

## Corner 3 — CONSTRAINTS -> V3

Inherited V2. Adversarial pass found the defect: supersession framing nailed
down earlier boot surfaces, violating the Operator's lift-up-never-nail-down
bar. Also flagged: hardcoded API keys in universal_memory_boot.py defaults.
V3: lineage reframed (chain elevates, never supersedes); key-rotation flag
raised; honesty constraints added (receipt freshness vs file existence).

## Corner 4 — RESOURCES -> V4

Inherited V3. Executed with real commits:

    GlacierEQ/aspen-grove-core 82f717a  chain orchestrator + contract
    GlacierEQ/apex-boot-core   67a784f  counterpart contract (Stage 3 role)
    GlacierEQ/aspen-grove-core 3c3e07c  lineage reframe (elevate, not supersede)
    GlacierEQ/apex-boot-core   a68798c  lineage reframe counterpart

## CENTER POINT

Integrated: both heads now reference one contract. Verified: GitHub returned
commit SHAs for every push; the local skill validator rejected a malformed
frontmatter write and accepted the corrected one. Remaining work (active
continuation, not completion): run the chain end-to-end in the estate
environment; rotate the flagged keys into OperatorKeyVault.

## Counterexample — false completion

A boot surface that slept and logged "OPERATIONAL" without probing anything:
its intent preceded its verification, and a prose log claimed a state no
receipt could support. The Center Point exists to stop exactly that.
PROCESSING_COMPLETE was never MISSION_COMPLETE. The chain's gates now make
that distinction machine-enforceable, carrying the earlier surface's intent
forward with the proof it always wanted.
