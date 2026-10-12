# Progressive Pyramid — one source, verified host projections

Canonical owner: `GlacierEQ/mega-skills`.
Source: `skills/progressive-pyramid/SKILL.md` and `progressive_pyramid.contract.json`.
Historical persona Four Corners lineage is separately retained in
`GlacierEQ/elysium-hub/personas/4corner_protocol.py`; the Context/Objective/
Constraints/Resources iteration is an execution projection, not an erasure
of that lineage.

## Install or audit a known GitHub checkout

Clone or fetch this repository through a version-controlled, authenticated
route on each device. Obtain the exact source commit SHA. Then, from the repo:

```bash
python3 scripts/install_progressive_pyramid.py --install --targets omp codex claude
python3 scripts/install_progressive_pyramid.py --check --targets omp codex claude
python3 -m unittest discover -s skills/progressive-pyramid/tests -v
```

`--targets` selects independent host projections. Defaults:
- OMP: `~/.omp/agent/managed-skills/progressive-pyramid`
- Codex: `~/.agents/skills/progressive-pyramid`
- Claude: `~/.claude/skills/progressive-pyramid`

Installed files include the canonical Skill/contract and a source revision.
Existing, unmanaged installations are never overwritten. For a managed
version update, use `--update`, which checks the prior source manifest,
refuses unrecorded edits, preserves a versioned backup and installs
the new canonical package. Legacy installs without a manifest may
be upgraded only if their content is identical to the current source.

```bash
python3 scripts/install_progressive_pyramid.py --update --targets omp codex claude
python3 scripts/install_progressive_pyramid.py --check --targets omp codex claude
```

Installation and content-hash equality are *not* cold-start load proof.
For each agent host, record its startup resolution of the exact source SHA,
the 7 certification-case outputs, a real continuation handoff, and an
independently verified outcome. Never report a host as certified on the
strength of local filesystem presence or unit tests alone.

## Boundary between processing and mission completion

The local validator checks sequence, inherited references, preserved gain
IDs, and evidence coverage. Self-attested outcome proofs fail terminal
verification. The actual host must inject a provider-aware verifier
for the specific mission outcome, as detailed in the canonical Skill.

APEX and Spiral may consume this Skill through compatible host adapters,
but their live integration is NOT implied by its publication or installation.
The original mission outcome and independent provider readback remain
the terminal authority. Case/private material belongs in its owning case
repo and provider evidence systems, never the shared Skill.
