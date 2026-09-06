---
name: genius-mastery
description: >
  Family kernel for Genius repositories — validate, doctor, synthesize, vector,
  and receipt. Use when the user says genius mastery, Genius-Mastery, mastery-not-skills,
  forge a Genius entity, or /genius-mastery. Do not use to dump the skill catalog
  or clone the whole GlacierEQ account.
---

# Genius-Mastery

Canonical kernel: `GlacierEQ/Genius-Mastery` (local `APEX_SYSTEM/INFRASTRUCTURE/Genius-Mastery`).
Doctrine: **mastery-not-skills**. This Skill routes to that kernel; it does not copy it.

## When

- Validate or doctor a Genius repo
- `genius name` / `genius new` / `genius synthesize`
- Buildkite native verify on `macos-self` (OCI `glacier-agent`)
- Plant or compose Genius entities into Tower / mega hierarchy

## Mind chassis (do not copy these skills)

| Need | Skill | Law |
|---|---|---|
| What do I know? | `epicenter` | L0 presence, L1 structure, L2 behavior. Untagged “facts” are illegal. |
| May I act? | `epistemic-gate` | Local work ≥ L2. Enterprise ≥ L5. Stubs forbidden. |
| How do I build? | `helix-pro-code` | Gap analysis, one push, verify-readback. Not a skill dump. |
| May I say done? | `verification-before-completion` | Fresh command output this turn, or the claim is false. |

Combo that orders them: `genius-epistemic-engineering`. Mega: `apex-genius-mastery`.

## Procedure

1. Prefer the live kernel, not this file: `genius --version` then `genius validate .` and `genius doctor .`.
2. Classify every claim with `epicenter` before engineering. `epistemic-gate` denies below L2.
3. All coding goes through `helix-pro-code`. Do not dump TDD/debug catalogs; load them only when that step needs them.
4. Evidence is claim+vector, never a single mastery percentage. No done-claim without `verification-before-completion`.
5. Tests: `pytest -q` in the Genius-Mastery tree (75 passed on glacier-agent 2026-09-04).
6. Receipts go to `evidence/receipts/` in the kernel, or `glacier-artifacts` on OCI.

## Paths

| Surface | Path |
|---|---|
| Kernel | `/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/Genius-Mastery` |
| GitHub | `https://github.com/GlacierEQ/Genius-Mastery` |
| OCI runner | `ubuntu@139.177.98.224:~/work/Genius-Mastery` |
| Tower exhibits | `tower_of_babel/the-tower-of-babel/languages/genius-mastery/` |

## Output contract

A Genius-Mastery receipt: validate PASS, doctor output, pytest count, or `VECTOR.yaml` integrity. Link the kernel; do not paste the anatomy.

## Local validation

`genius validate .` PASS and `pytest -q` green in the kernel tree.

## Non-goals

Do not dump 700 atomics, clone the full GitHub account, or put CYBERTACK exhibits on the public OCI IP. Do not emit a fake mastery percentage.
