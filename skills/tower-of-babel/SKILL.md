---
name: tower-of-babel
description: "Operating inside the Tower of Babel polyglot technology authority at /root/projects/GlacierEQ_Swarm/the-tower-of-babel. Use when changing the registry, adding a floor, updating exhibits, changing proof state, or generating surface artifacts. Tower has its own doctrine and a mandatory preflight — violations break the evidence chain."
---



# Tower of Babel Skill

Governed polyglot technology authority and execution proof system. 40 floors
across 8 categories (SYS, ORCH, DATA, GPU, IDL, HW, FORMAL, NEXTGEN). Each
floor has a registry entry, two exhibits (easy + advanced), a proof gate,
and a Megamind agent/piston assignment.

**Do not duplicate Tower doctrine here — the AGENTS.md in the project is
the authority. This skill is a routing + discipline aid.**

## Project Layout

| Path | Purpose |
|------|---------|
| `registry/tower.yml` | The authority. The single source of truth for all 40 floors. **Never hand-edit downstream artifacts without this changing first.** |
| `src/tower/` | Implementation: registry, validation, generation, integrity |
| `languages/` | Per-language artifacts (CUDA, Rust, Lean, etc.) |
| `governance/` | Tower governance files |
| `integrations/` | Aspen Grove bridges |
| `tests/` | 22 test files |
| `pyproject.toml` | `tower` and `tower-activate` CLI entry points |
| `lakefile.lean` | Lean 4 build |
| `build.sbt` | Scala (Chisel) build |

## Entry Points (CLI)

```bash
cd /root/projects/GlacierEQ_Swarm/the-tower-of-babel

tower validate                     # registry check
tower generate --check             # surface gen
tower integrity verify             # adversarial check
tower spec <floor>                 # floor detail
tower build <floor>                # compile
tower benchmark <floors>           # perf
tower megamind-map                 # agent export
tower spiral question --seed X --prompt-hint "Y"
tower preflight --mission "..." --memory <mem.json> --require-memory   # MANDATORY before non-trivial change
```

## Test Command

```bash
cd /root/projects/GlacierEQ_Swarm/the-tower-of-babel && pytest
```

The Tower AGENTS.md prescribes an 8-step workflow ending in
`tower preflight`, `tower validate`, `tower generate`, `pytest`,
`tower build --all --allow-blocked`, integrity verification, and
deterministic receipt generation. Follow that order. Don't reorder it.

## Hard Rules (Non-Negotiable, from project AGENTS.md)

1. **The registry (`registry/tower.yml`) is the technology-evidence
   authority.** Do not add a language, format, compiler, HDL, proof system,
   or runtime by editing the README, sidecar, generated files, or
   Megamind maps directly. Update the registry first.
2. **Run `tower preflight` before any non-trivial change.** The receipt
   goes to `artifacts/resource-memory-preflight.json`. Skipping this is
   a Doctrine violation.
3. **Reuse or extend the strongest prior verified lane** instead of
   restarting it. `LAST_VERIFIED_STATE + NEW_VERIFIED_DELTA` is the
   default evolution model.
4. **Never promote a floor without corresponding evidence.** A filename
   containing "advanced" does not establish production maturity. Use the
   declared evidence state (illustrative, compiles, tested, benchmark,
   hardware_gated, toolchain_gated, service_gated, formally_verified,
   integrated, production_reference).
5. **Generated files must not be hand-edited.** They are overwritten by
   `python3 -m tower.generate`. If you need to change a generated file,
   change the source it generates from and re-run the generator.
6. **A failed search does not prove prior work never existed.** Repeated
   copies of the same bytes remain one evidentiary lineage. Collapse
   duplicates before counting them as corroboration.
7. **A counterexample or contradiction is preserved until resolved; it
   is not deleted to make a technology look stronger.**

## When to Use This Skill

- Adding a floor (new language, format, compiler, HDL, proof system)
- Changing a floor's evidence state, proof class, or exhibit paths
- Adding/updating interfaces, architecture lanes, or admission status
- Running the `tower spiral` command sequence
- Generating the deterministic receipt after a build

## When NOT to Use This Skill

- Pure monorepo work that doesn't touch a floor (rare)
- Editing downstream projects — Monolith is upstream of them, not Tower
- Work that requires hand-editing a generated file (you have a design
  problem if you need to do this)

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Skip `tower preflight` | critical | Doctrine violation. Always run before non-trivial change. |
| Hand-edit a generated file | critical | Change the source-of-truth, re-run `tower generate`. |
| Edit `README.md` or sidecar to add a language | critical | Update `registry/tower.yml` first. The registry is the authority. |
| Promote floor without evidence | critical | Match declared evidence state; do not interpret filenames as evidence. |
| Forget to run `tower validate` after registry edit | high | `tower validate` is the cheapest integrity check. |
| Two `pyproject.toml` files (this project + Make-It-Heavy) confusing tools | medium | Each project has its own; always `cd` to the project root first. |
| Use `pytest tests/` without `tower preflight` first | high | Tower workflow: preflight → registry → exhibits → proof gate → validate → generate → pytest → build → receipt. |

## Evidence States Quick Reference

```
i   illustrative
c   compiles
t   tested
b   benchmark
hg  hardware_gated
tg  toolchain_gated
sg  service_gated
fv  formally_verified
ig  integrated
pr  production_reference
```

## Proof Classes Quick Reference

```
i       illustrative
compile compile
bv      behavioral
benchmark benchmark
hw      hardware
ig      integration
formal  formal
```

## Related Skills

- `apex-sovereign-runtime` — receipt-chain doctrine (Tower uses receipts too)
- `monolith` — Monolith governs downstream projects but is independent of Tower
- `architecture` — for ADR-shaped decisions about new floors
- `clean-code` — pragmatic style for Tower's own Python
- `security-review` — for any change involving network/toolchain access

## Token Optimization Note

The Tower AGENTS.md is already token-optimized (~75% savings vs standard
docs per the Aspen Grove bridge). Don't paraphrase or summarize it
in-line; load it directly when in this project.
