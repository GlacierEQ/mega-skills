# OMP × GlacierEQ: Native Power-Skill Activation

**Ownership:** This is an additive target of the existing sync_runtime_skills.py. Mega-Skills remains the canonical source for atomic, Compound, and Mega contracts. OMP is a native consumer, not a replacement orchestrator.

## Recovered power coalition

The mission-ready activation selects **38 source-linked Skills**: 28 active atomics (including eight additive Apple-platform specialists), four active Compound Skills, and six active Mega Skills. This is a starting coalition, **not a hard skill-count ceiling**.

- **Mission/authority:** power-skill, casey-operator-execution-kernel, capability-admission, strong-smart-routing-kernel, apex-aspen-grove-bootup, apex-meta-skill-kernel
- **Reasoning/engineering:** genius-mastery, codemaster, make-it-heavy, systematic-debugging, test-driven-development, verification-before-completion, progressive-pyramid
- **Mac/iOS native intelligence:** desktop-commander-overview, re-apple-bundles, swiftui-patterns, swift-concurrency-6-2, xcode-project-setup, mobile-design, foundation-models-on-device, ios-icon-gen
- **Memory/continuity/MCP:** skill-connector-router, unified-memory-connect, agent-memory-systems, spiral-promotion-gate, computer-user-core, apex-universal-mcp-powerhouse, mcp-architect
- **Compound mission workflows:** genius-epistemic-engineering, apex-mesh-dispatch, strong-smart-execution-stack, cross-cloud-memory-synthesis
- **Mega mission workflows:** apex-genius-mastery, apex-strong-smart-execution-engine, apex-dev-fork-orchestrator, apex-orchestrator-mesh, far-away-party, apex-self-healing-forge

These names are resolved from existing canonical directories. Active source maturity was inspected against repository registries; candidate-only Mega Skills are excluded from initial activation. The entire skill graph remains available for mission-specific composition; no specialist-count gate may truncate required mission coverage.

## Evidence-aware selector (T1) and static baselines

The default command below still uses `OMP_POWER_SELECTION` unchanged. On this revision that constant is the 38-skill list, because the eight Apple/macOS/iOS atomics from PR #56 are already on main. Comparison names:

- **B1** is the frozen 30-skill coalition from PR #51 (merge `da26fa48`): 20 atomics, 4 compound skills, and 6 mega skills. It does not include the Apple platform atomics. The list lives in `scripts/skill_evidence_selector.py` as `B1_COALITION`.
- **B2** is today's `OMP_POWER_SELECTION`: B1 plus `desktop-commander-overview`, `re-apple-bundles`, `swiftui-patterns`, `swift-concurrency-6-2`, `xcode-project-setup`, `mobile-design`, `foundation-models-on-device`, and `ios-icon-gen`.
- **T1** is opt-in. `--select evidence` reads a task descriptor plus the append-only ledger, then passes that coalition into the existing `sync_omp_skills(..., selection=...)`. Preflight, no overwrites, rollback on failed readback, and write-free preview stay in the installer.

T1 scores a task family by pass/fail, regressions, mean wall time, and a cost proxy. The cost proxy is the sum of canonical contract bytes: `SKILL.md` for atomics, `COMBO.md` for compound skills, and `MEGA.md` for mega skills. Catalog prestige and skill count do not raise a score. A skill outside B1 is added only when that family's utility is positive. A skill marked harmful or conflicting for that family is removed. Rows from another family do not transfer. If the family has no usable evidence, T1 returns B1 unchanged and sets `decision` to `no evidence`. It does not invent a new default bundle.

`evidence/skill-selection/ledger.json` is schema version 1 and append-only. Every committed row is a fixture seed (`production_outcome` false, label states it is not a production outcome). Labeled tasks, including the generic Python repair case, the ledger-reuse follow-up, the withheld Apple/cloud specialist, the single Apple atomic, the harmful-skill exclusion, profile collision, bad identifiers, missing sources, and the no-evidence fallback, live in `tests/fixtures/skill_selection_tasks.json`. Verified fixture metrics and command receipts for this OMP selector live in `ops/receipts/evidence-aware-skill-selector-omp.json` (distinct from `scripts/evidence_capability_selector.py` and `ops/receipts/evidence-capability-selector.json`).

Proof commands from a checkout of this revision:

    python3 -m unittest discover -s tests -p 'test_omp_native_sync.py' -v
    python3 -m unittest discover -s tests -p 'test_skill_evidence_selector.py' -v
    python3 -m compileall -q scripts tests
    python3 scripts/validate_hierarchy.py

Write-free evidence preview against a temporary directory, not a live OMP profile:

    python3 scripts/sync_runtime_skills.py --runtime omp --omp-skills-dir /tmp/omp-skill-preview --select evidence --task-json tests/fixtures/skill_selection_tasks.json --task-id evidence-insufficient

This selector does not certify a host OMP install and it does not report Phase 2 engineering-quality results. Local unit output is the proof available here. Hosted GitHub Actions on this private repo currently exit in a few seconds with zero steps (issue #23). That account-level blocker is unchanged.

## Inspect the actual OMP profile before applying

OMP's default user profile is typically ~/.omp/agent. Named profiles use ~/.omp/profiles/NAME/agent, and project-level .omp configuration may override user settings. Confirm the actual root with OMP's own profile/runtime tools before applying.

From a checked-out Mega-Skills repository at the intended revision:

    python3 scripts/sync_runtime_skills.py --runtime omp --omp-skills-dir "$HOME/.omp/agent/skills"

This is **preview-only**, returns per-item planned/existing/conflict/missing state and SHA-256 of each current source contract, and does not create the OMP skills directory.

After inspecting the preview and selecting the correct profile, apply only missing links/adapters:

    python3 scripts/sync_runtime_skills.py --runtime omp --omp-skills-dir "$HOME/.omp/agent/skills" --apply

Apply first preflights the entire coalition. A source conflict, missing file, or invalid native metadata prevents every write; a simulated or actual install/readback failure triggers ownership-checked rollback for newly created entries, never deletion of pre-existing skill directories. A nonzero return indicates a missing source, collision, installation error, or unsuccessful readback. A collision is reported, not silently overwritten. The synchronizer never deletes or retires existing OMP skills. Atomic Skills point directly at canonical skill directories. Compound and Mega Skills use native SKILL.md adapters with source-linked COMBO.md/MEGA.md; changed source that invalidates an existing adapter is reported as drift/conflict, not silently rebaselined. The returned per-item SHA-256, created/rolled_back status, and blocked_preflight/verification_failed flags let CI and host operators independently reconcile the attempt.

**Upstream OMP discovery proof:** Current native `scanSkillsFromDir` enumerates immediate children with `isDirectory()` **or** `isSymbolicLink()`, then checks each `SKILL.md`. Native source discovery requires `description` frontmatter. The activation tool now detects missing native description and returns `invalid_source` instead of silently installing an undiscoverable skill. All 28 selected atomic entrypoints were independently inspected for a non-empty description; all passed. See `https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/discovery/helpers.ts` and `https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md`. This is upstream source verification, not a local OMP host activation claim.

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

Focused source-check commands (provider execution still required for actual changed branch):

    python3 -m unittest discover -s tests -p 'test_omp_native_sync.py' -v
    python3 -m compileall -q scripts tests

Red-before-green reproduced missing native OMP activation. Nineteen committed focused regressions cover preview/no-write, additive symlinks/adapters, **whole-coalition preflight**, idempotence, missing sources, unrelated profile preservation, identifier/path rejection, changed-source detection, untrusted symlink preservation, OMP-required descriptions (including multiline YAML), **simulated mid-install failure rollback**, **post-install readback rollback**, no arbitrary skill cap, and cross-checks for source drift during write, unexpected adapter readback, and concurrent modifications during rollback.

**Release proof ladder:**
1. Exact branch blob hashes match locally tested bytes; upstream hierarchy and native CI pass.
2. Confirm real target OMP profile, effective tool/skill discovery and existing skills before host changes.
3. Run preview; reconcile every missing/conflicting source; apply additively; inspect OMP-native skill discovery.
4. Recover authenticated APEX/Spiral mission through native hook; select capable composition for real current intent.
5. Execute authorized provider operation via Computer User with independent readback and durable receipt.
6. Kill/restart OMP process, recover exact cursor, demonstrate Mission 2 benefits from extracted capability.
7. Complete existing 20-task action-quality evaluation: at least 90/100, zero critical authority, replay or evidence-integrity failures.

**Current proof:** original activation behavior independently replayed in a local Python fixture (15/15 checks passing), with the 18-case regression suite committed and source-read-back from GitHub. The exact full branch suite remains pending native CI/checkout execution; profile bootstrap has a separate exact-byte-tested 11-case suite on Computer User PR #84. Mac host and external OMP installation have not been verified here. Do not claim an operational release from files, links, skill listings, or passing isolated tests.
