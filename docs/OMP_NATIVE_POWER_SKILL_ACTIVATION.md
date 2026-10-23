# OMP × GlacierEQ: Native Power-Skill Activation

**Ownership:** This is an additive target of the existing sync_runtime_skills.py. Mega-Skills remains the canonical source for atomic, Compound, and Mega contracts. OMP is a native consumer, not a replacement orchestrator.

## Recovered power coalition

The initial mission-ready activation contains **30 source-linked Skills**: 20 active atomics, four active Compound Skills, and six active Mega Skills. This is a starting coalition, **not a hard skill-count ceiling**.

- **Mission/authority:** power-skill, casey-operator-execution-kernel, capability-admission, strong-smart-routing-kernel, apex-aspen-grove-bootup, apex-meta-skill-kernel
- **Reasoning/engineering:** genius-mastery, codemaster, make-it-heavy, systematic-debugging, test-driven-development, verification-before-completion, progressive-pyramid
- **Memory/continuity/MCP:** skill-connector-router, unified-memory-connect, agent-memory-systems, spiral-promotion-gate, computer-user-core, apex-universal-mcp-powerhouse, mcp-architect
- **Compound mission workflows:** genius-epistemic-engineering, apex-mesh-dispatch, strong-smart-execution-stack, cross-cloud-memory-synthesis
- **Mega mission workflows:** apex-genius-mastery, apex-strong-smart-execution-engine, apex-dev-fork-orchestrator, apex-orchestrator-mesh, far-away-party, apex-self-healing-forge

These names are resolved from existing canonical directories. Active source maturity was inspected against repository registries; candidate-only Mega Skills are excluded from initial activation. The entire skill graph remains available for mission-specific composition; no specialist-count gate may truncate required mission coverage.

## Inspect the actual OMP profile before applying

OMP's default user profile is typically ~/.omp/agent. Named profiles use ~/.omp/profiles/NAME/agent, and project-level .omp configuration may override user settings. Confirm the actual root with OMP's own profile/runtime tools before applying.

From a checked-out Mega-Skills repository at the intended revision:

    python scripts/sync_runtime_skills.py --runtime omp --omp-skills-dir "$HOME/.omp/agent/skills"

This is **preview-only**, returns per-item planned/existing/conflict/missing state and SHA-256 of each current source contract, and does not create the OMP skills directory.

After inspecting the preview and selecting the correct profile, apply only missing links/adapters:

    python scripts/sync_runtime_skills.py --runtime omp --omp-skills-dir "$HOME/.omp/agent/skills" --apply

A nonzero return indicates a missing source, collision, or installation error. A collision is reported, not silently overwritten. The synchronizer never deletes or retires existing OMP skills. Atomic Skills point directly at canonical skill directories. Compound and Mega Skills use native SKILL.md adapters with source-linked COMBO.md/MEGA.md; changed source that invalidates an existing adapter is reported as drift/conflict, not silently rebaselined.

**Upstream OMP discovery proof:** Current native `scanSkillsFromDir` enumerates immediate children with `isDirectory()` **or** `isSymbolicLink()`, then checks each `SKILL.md`. Native source discovery requires `description` frontmatter. The activation tool now detects missing native description and returns `invalid_source` instead of silently installing an undiscoverable skill. All 20 selected atomic entrypoints were independently inspected for a non-empty description; all passed. See `https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/discovery/helpers.ts` and `https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md`. This is upstream source verification, not a local OMP host activation claim.

**Provenance boundary:** emitted SHA-256 values describe source bytes at inspection time. Source symlinks are *not* immutable revision pins. Lock repository revision and verify provider-native state before promoting to host-certified operation.

## Native integration boundary

- OMP native boot/mission candidate: existing Computer User PR #84 (integrations/omp), separately reviewed and installed
- OMP MCP runtime: existing computer-user MCP facade and kernel, not an alternate engine
- APEX/Spiral: authoritative mission admission, corrected continuation and state
- Aspen/Context First: source-grounded context recovery and learning
- sigma-glue: workflow state, idempotency, ambiguity reconciliation
- Genius-Mastery/Mega-Skills: skill source, routing/composition and capability extraction
- Computer User: authorized action execution, receipts and provider readback

This activation does not overwrite RULES.md, AGENTS.md, MCP profile/config, sessions, extensions, or existing skill directories; nor does it automatically invoke provider mutations, authorize missions, install OMP, or deploy the host.

## Evidence and release requirements

Local focused test commands:

    python -m unittest discover -s tests -p 'test_omp_native_sync.py' -v
    python -m compileall -q scripts tests

Red-before-green reproduced missing native OMP activation. Twelve focused regressions cover preview/no-write, additive symlinks/adapters, collisions, idempotence, missing sources, unrelated profile preservation, identifier/path rejection, changed-source detection, untrusted symlink preservation, no arbitrary skill cap, and OMP-required description validation (including multiline YAML).

**Release proof ladder:**
1. Exact branch blob hashes match locally tested bytes; upstream hierarchy and native CI pass.
2. Confirm real target OMP profile, effective tool/skill discovery and existing skills before host changes.
3. Run preview; reconcile every missing/conflicting source; apply additively; inspect OMP-native skill discovery.
4. Recover authenticated APEX/Spiral mission through native hook; select capable composition for real current intent.
5. Execute authorized provider operation via Computer User with independent readback and durable receipt.
6. Kill/restart OMP process, recover exact cursor, demonstrate Mission 2 benefits from extracted capability.
7. Complete existing 20-task action-quality evaluation: at least 90/100, zero critical authority, replay or evidence-integrity failures.

**Current proof:** local unit/byte-compilation only until branch CI and real host readback. Mac host and external OMP installation have not been verified here. Do not claim an operational release from files, links, skill listings, or passing isolated tests.
