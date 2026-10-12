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

The Spiral Engine already distinguishes local quality completion from
mission-outcome completion; the Pyramid contract connects to that check. APEX
startup loads this skill; Spiral verification enforces the finish line.
