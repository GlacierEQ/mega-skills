# Hidden-Harm Audit — Operator Continuity + Antigravity CLI surface

**Audit date:** 2026-11-16 (Pacific/Honolulu)  
**Scopes:** `hidden-harm-context`, `hidden-harm-connectors`, `hidden-harm-github`, `hidden-harm-cross-domain`  
**Target:** continuity packet + Antigravity/AGY skill honesty (not a fleet-wide audit)

## Findings (pre-fix)

| ID | Pattern | Evidence | Harm if left | Remediation |
|---|---|---|---|---|
| HH-01 | Ephemeral path as durable authority | `HANDOFF.md` Memory triad still named `/home/ubuntu/.apex-session/env-part2.sh` as the staging location without marking session-local | Next chat treats missing file as “Part 2 never existed” (retrieval-as-absence) | Mark as originating-VM only; point to key *names* + Keymaster |
| HH-02 | Cross-branch false path | Resume step required `evidence/calibrator-chassis/pro-mastermind-reconnect.md` which exists only on `cursor/pro-mastermind-quality-processors-f969` (PR #62), not on `main` / this packet | Resume fails or invents “missing evidence” as fact | Gate: checkout/read that branch/PR before treating as present; else `RETRIEVAL_GAP` |
| HH-03 | False capability (AGY guide) | `skills/antigravity-guide/SKILL.md` mandates `references/cli.md` etc.; directory **absent**; tests never check | Agents “activate” AGY CLI guide that cannot load offline subdocs | Honesty rewrite: live docs are authority; offline refs = `OFFLINE_GAP` |
| HH-04 | False capability (agy-customizations) | `SKILL.md` links `./docs/*.md`; `docs/` **absent** | Same — customization guide overclaims | Honesty rewrite to live Antigravity docs URLs |
| HH-05 | Adapter ≠ execution | `antigravity-guide/skill.py` returns `capability_executed: false` — honest — but SKILL description implies comprehensive guide | Runtime exposure promoted to provider/product truth | Keep adapter honest; SKILL must not imply local CLI execution |
| HH-06 | Hardcoded Mac CLI (estate note) | Omnibus `antigravity_cli.py` binds `/Users/macarena1/...` paths | Portability trap (same class as old `MASTERMIND_HOME=/root/projects/mastermind`) | Document; do not treat as portable `agy` on this VM |
| HH-07 | Connector verification inflation | “SuperMemory primary” without “GET-by-id verified; search ranking may lag” | Search miss → false absence of continuity | Record verification scope: GET status=`done` for listed document ids |
| HH-08 | Machine-state gravity | Open asks / open PRs listed as if they are this turn’s mission | Easy-work capture (land PRs) displaces Operator ask (wire Mac / continuity / AGY) | Label as backlog; Operator next-action separate |
| HH-09 | Peak-language risk | “Cortex 6/12 live” without branch provenance in packet | Peak-restored narrative while 6 pistons dark | Cite PR #62 branch path; keep “still dark” list |

## Verification performed this audit

- Session env present on originating VM: yes (`env-part2.sh`) — **not portable**
- SuperMemory GET `Esmc3XxT3XvoYyU5rX2zrh`, `DFitxk6kZxDA2ezmJV3Q7B`: `status=done` with handoff content
- `pro-mastermind-reconnect.md`: **absent** on this branch/`main`; **present** on PR #62 branch tip
- `skills/antigravity-guide/references/`: missing
- `skills/agy-customizations/docs/`: missing
- `agy` / `antigravity` binaries: not on PATH in this cloud VM
- Mem0: Operator declined — not required for continuity

## Operator-aligned next action after scrub

Preserve continuity truth + AGY honesty so Mac Part 2 wire / chat resume cannot be derailed by false paths or fake offline AGY docs. Do **not** expand into 1400-repo theater.
