---
name: rea-operator
description: "Install, register, and operate REA (morluto/rea, npm rea-agents, MIT) as the estate's gated reverse-engineering backend: official channels only, version-pinned, doctor/setup plan-approve-apply, MCP registration, compact-schema profile, and the connection-and-recovery ladder."
---

# REA Operator

Own the REA installation and operation discipline — REA (Reverse Engineer Anything, by morluto; MIT License) is the estate's reverse-engineering execution backend, and this skill is the only sanctioned way it enters the estate.

## Workflow

1. Acquire only from official channels: the GitHub repository `morluto/rea`, `rea.tools`, or the npm package `rea-agents`. Anything else is a copy — malicious lookalikes carrying installer tags are already in the wild, and a copied README does not make a download official.
2. Pin the version. Record the exact `rea-agents` version in the registration receipt; never float on `@latest` for a registered server.
3. Diagnose before repairing: `npx -y rea-agents@<pinned> doctor --client <client> --format json`. Doctor inspects registration; it cannot prove the current session is connected.
4. For a configuration repair, prepare the read-only plan first — `setup --client <client> --dry-run --format json` — show exact paths, backups, and the bundled-skill replacement, and obtain approval before setup writes anything. Apply the approved scope with `setup --client <client> --yes`; add `--install-hopper` only when that separate install was explicitly approved.
5. Restart/reconnect the client and verify REA tools actually appear in the session before declaring registration done.
6. Prefer the compact input-schema profile for routine work: the full 207-tool handshake is context-expensive (measured ~200K tokens of schemas; the compact profile cuts it to ~55K). Load the full surface only when a task needs it.

## The recovery ladder

Client approval, shell PATH, registration, and engine availability are different failures with different remedies — never repeat setup for all of them. A dropped MCP connection gets one retry when the call is safe to repeat or known not to have started; if it may already have changed the target, stop and ask for a client restart. A host timeout with no REA result does not mean work stopped — check the deadline distinction before repeating an unchanged call. REA setup never installs or upgrades Node.js, npm, Homebrew, Java, Ghidra, IDA, JADX, Kuna, Binwalk, or Unblob.

## CLI fallback

When MCP is unavailable but package acquisition is in scope, the CLI runs the same workflows: `npx -y rea-agents@<pinned> analyze-javascript-application /absolute/path/to/app --format json` returns the Evidence record directly for a JavaScript tree or ASAR. A CLI result does not establish that MCP is configured; native CLI tasks still require their selected engine.

## Safety gates

- Official channels only, pinned versions only — no exceptions, no mirrors, no lookalike repositories.
- Setup writes happen only after a reviewed dry-run plan and explicit approval, with backups preserved.
- Never disable a client sandbox or approval policy to make registration "work"; preserve the boundary and repair the actual blocker.

## Output contract

- Registration receipt (client, pinned version, paths, backups)
- Doctor/session verification showing tools present, or the named blocker with its remedy

## Related skills

- re-target-triage — the first move once REA is connected
- re-safety-gate — authorization precedes any target work
- re-engine-bridges — the bring-your-own engines REA drives
- reverse-engineering-pipeline — the combo this skill serves

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/rea-operator/tests -v
git diff --check
```
