---
name: dependency-update-operator
description: "Operate dependency updates as a governed pipeline: Dependabot baseline via .github/dependabot.yml plus Renovate configuration patterns (grouping, schedules, automerge rules) reimplemented estate-side. Renovate is AGPL-3.0: run it as a tool or service only; never lift its code."
---

# Dependency Update Operator

Keep estate dependencies current through automated, grouped, scheduled update pull requests whose candidates enter the Spiral Promotion Gate before merge — closing the registry's dependency-automation gap without inventing a new tool.

## Workflow

1. Inventory the estate's repositories by ecosystem; record which already have update automation and which have none.
2. Enable the Dependabot baseline per repository (dependabot.yml committed to main) with a weekly schedule and per-ecosystem directories.
3. Layer grouping/schedule/automerge policy as Renovate configuration where it runs as a service, or as estate-side configuration expressing the same patterns where it does not.
4. Route every update PR into the candidate ledger; classify patch/minor/major and attach CI status.
5. Automerge only the classes the estate rule names (patch-level, green CI, non-framework); everything else goes to spiral-promotion-gate with evidence.
6. Review the ledger on cadence: merged, gated, stale, and failing candidates each get a recorded disposition.

## Two layers, one policy

This skill closes the registry gap named in the composed upgrade set: no dependency-update automation existed. It builds the capability from two existing layers — no new tool is invented.

- **Baseline: Dependabot.** GitHub's native dependency and security updates, enabled per repository with `.github/dependabot.yml` (ecosystem, directory, schedule). Zero-install, platform-maintained; the default for every repository.
- **Control layer: Renovate patterns.** Renovate (source: `renovatebot/renovate`, **AGPL-3.0**) may be *run* as a hosted tool/service, but its code is never lifted into the estate. What this skill reimplements — as original estate configuration, with attribution to the Renovate documentation's published concepts — are its *configuration patterns*: grouping related packages into one PR, scheduling update windows, automerge rules for low-risk classes (patch/dev-dependency), and PR limits to prevent queue floods.
- **Candidates, not merges.** Automation opens candidates; the Spiral Promotion Gate decides. Patch-level, test-green updates may automerge under an explicit estate rule; majors and framework bumps always wait for the gate.

## Safety gates

- Never copy Renovate source code into the estate (AGPL-3.0); patterns and configuration concepts only, with attribution.
- Never automerge a major version, a framework, or a security-sensitive package (auth, crypto, serialization) — those always pass the promotion gate.
- Update automation that produces unreviewed PR floods is a failure mode: PR limits and grouping are mandatory, not tuning.

## Output contract

- Per-repository dependabot.yml and/or renovate configuration, committed
- Update-candidate ledger feeding spiral-promotion-gate decisions

## Related skills

- spiral-promotion-gate — decides which update candidates are promoted
- automated-security-scanning — the vulnerability lane that prioritizes security updates
- managing-python-dependencies — project-scoped dependency discipline for Python repos
- release — version and artifact mechanics after a promoted update

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/dependency-update-operator/tests -v
git diff --check
```
