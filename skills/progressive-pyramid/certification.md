# Progressive Pyramid Certification Suite

Shared certification for every agent runtime claiming Pyramid compliance
(Codex / OpenAI agents, Claude agents, OMP / local agents, MCP-enabled agents,
APEX + Spiral acceptance). Identical missions and identical machine-readable
criteria across agents. Identical criteria, not identical prose: an
engineering agent and a legal research agent may hold different domain
expertship but are judged by the same inheritance, evidence, continuation,
and completion rules.

## Test matrix

| Test | Required behavior | Machine-readable criterion |
|---|---|---|
| Fresh session | Recover prior state without asking the Operator to repeat it | mission_init cites recovered sources; zero re-requested known context |
| Inheritance | V2, V3, V4 demonstrably retain valid previous work | each stage output references its inherited lineage; no dropped gains |
| Contradictory evidence | Correct the affected conclusion without destroying unrelated gains | correction receipt present; unaffected lineage entries intact |
| Recursive work | Return completed child results to the parent | parent mission cites child mission output and validation |
| False completion | Reject "mission complete" when only a draft, PR, or test exists | MISSION_COMPLETE claim blocked unless acceptance criteria evidenced |
| Cross-agent handoff | A second agent continues the same mission and artifact lineage | continuation state consumed; lineage preserved; no restart from zero |
| Terminal outcome | Require independent evidence of actual completion | source-native receipts for each acceptance condition |

## Judging

Each test passes or fails on the criterion, never on prose similarity.
Failures record the exact stage, the expected criterion, and the observed
result. A runtime is certified only when all seven pass on identical missions.

## Alignment

The Spiral Engine's mission-bound improvement contract already distinguishes
local quality completion from mission-outcome completion. The Progressive
Pyramid's independent contract has compatible intended semantics, but that
does **not** prove a live integration. APEX startup and Spiral runtime adapters
must be independently inspected, wired to the canonical version-pinned Skill,
and tested before any host can be described as enforcing this protocol.

## Evidence boundary and deployment state (2026-10-11 HST)

- VERIFIED SOURCE: `skills/progressive-pyramid/SKILL.md` and its JSON contract,
  certification specification, and worked example are committed in this repo.
- NOT YET VERIFIED: a fresh APEX startup automatically loads this canonical
  Skill and rejects an invalid stage/output.
- NOT YET VERIFIED: Spiral invokes this exact contract and blocks false
  MISSION_COMPLETE through independent outcome evidence.
- NOT YET VERIFIED: Codex, Claude, OMP, and MCP hosts have each executed and
  passed the seven tests on identical missions.
- NOT EQUIVALENT: the seven-row *specification* is not an executable certification
  harness, and local mounting in one session is not universal cross-device load.
- REQUIRED EVIDENCE: for each host, pin source commit and contract digest; run a
  cold-start recovery exercise, V1→V4 inheritance exercise, contradiction
  correction, subordinate return, false-finish denial, cross-agent resumption,
  and independently witnessed terminal outcome. Save source-native receipts and
  the exact failing or passing version.
- REGISTRY: `scripts/generate_mega_skill_pyramids.py --check` compares an
  existing graph against its registries; it does not create missing Skill
  registration. Registry membership and readiness must be verified separately.

Only report `CERTIFIED` for a specific versioned runtime after the complete
suite passes with recorded evidence. Otherwise report `NOT_VERIFIED` or a
specific failing test, preserve the original mission, and continue.


## Executable local gate and registry readback (2026-10-11 HST)

The canonical Skill now includes a provider-verifier-injected machine gate at
`scripts/validate_run.py` and 12 deterministic behavioral tests under
`tests/test_validator.py`. These prove structural inheritance/continuity and
that MISSION_COMPLETE is rejected without an independent verifier.

The atomic Skill registry includes `progressive-pyramid`; the generated
recursive graph is refreshed from source registries. Package-local tests also
cover the formerly unverified strong-smart-routing-kernel and github helpers.
Readiness classification distinguishes those local behaviors from live
network/runtime certification.

These are LOCAL CODE AND REGISTRY VERIFICATIONS, not evidence of automatic
Codex/Claude/OMP startup injection or verified external mission outcomes.
The seven cross-host certification cases remain unexecuted until each host's
receipts are gathered. Do not promote local unit tests into host certification.
