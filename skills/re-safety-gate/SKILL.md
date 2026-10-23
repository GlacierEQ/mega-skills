---
name: re-safety-gate
description: "The authorization and safety gate for all reverse-engineering work: owned-or-authorized targets only, REA's disclaimer exclusions enforced, executesForeignCode/destructive tool flags honored, throwaway environments for runtime work, and official-channel-only tooling."
---

# RE Safety Gate

Own the gate. No reverse-engineering work in this estate starts until authority, scope, and environment are established — REA's own DISCLAIMER.md and SECURITY.md are the floor, and this skill enforces them as estate law.

## Workflow

1. Establish authority: the target is software the operator owns or is authorized to examine (security research, malware/incident analysis, vulnerability research, CTF/education, interoperability, preservation, debugging). Record the basis before any tool runs.
2. Apply the exclusion list verbatim from REA's disclaimer — the gate refuses: circumventing DRM, license checks, anti-cheat, or other technical protection measures; developing game cheats or tampering with online services; bypassing authentication, bot protection, or access controls on systems the operator is not authorized to test; copying proprietary software or reproducing its protected code and assets; evading AI provider usage policies; reselling or sharing AI accounts or API access.
3. Separate inspection authority from execution authority: authorization to inspect an artifact does not by itself authorize executing it, intercepting its traffic, or changing a connected device. Each is gated on its own.
4. Classify planned operations by REA's tool-effect flags: anything marked `executesForeignCode` or carrying a destructive hint runs only against owned/authorized targets inside a throwaway environment, with the host client's confirmation as the operative control — REA has no per-call approval of its own.
5. Confine the blast radius: Ghidra work happens in REA's isolated temporary project (deleted on close); runtime targets run in a disposable VM/container identity, never the operator's daily environment.
6. Record the gate decision in the investigation ledger (re-evidence-record) before the first analysis call.

## REA is not a sandbox

SECURITY.md states it plainly: bridge capability tokens and isolated projects limit accidental persistence and resource use; they do not make analysis safe against a hostile binary. Opening an untrusted binary delegates parsing to the selected local provider with the operator's permissions. Treat every unknown target as hostile until evidence says otherwise.

## Two standing cautions

- Findings flow to the agent's model provider: analysis is local, but the evidence the agent reads goes wherever its LLM lives. Flag targets whose contents must not leave the machine before work begins.
- Tooling comes only from official channels (rea-operator): a lookalike REA installer is itself a hostile-binary scenario.

## Safety gates

- No authority record, no analysis. No exceptions for "just a quick look" — triage of identity is the only pre-gate act.
- Excluded purposes are refused, not renegotiated per target.
- Runtime execution outside a throwaway environment is refused.

## Output contract

- Gate decision recorded in the ledger: authority basis, authorized scope, exclusions applied, environment
- Effect classification for every executing or destructive operation in the plan

## Related skills

- rea-operator — official-channel acquisition and setup approval
- re-dynamic-analysis — the lane that executes targets, always behind this gate
- re-evidence-record — where the gate decision is recorded
- re-untrusted-content-defense — the companion discipline for target-derived content

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-safety-gate/tests -v
git diff --check
```
