---
name: re-dynamic-analysis
description: "Runtime reverse engineering with REA: Frida instrumentation, LLDB/GDB/pwndbg debugging, process capture, and recorded-crash (core dump) analysis — the lane that executes targets, always behind the safety gate in a throwaway environment."
---

# RE Dynamic Analysis

Own the lane that runs the target. Everything here executes foreign code or attaches to it: this skill operates only behind a re-safety-gate decision, inside the throwaway environment the gate named, and its outputs are runtime observations — a distinct evidence class from every static lane.

## Workflow

1. Justify runtime work: static evidence must have left a specific question open (REA's own planning rule: corroborate with the evidence type the conclusion requires; use runtime observation only when static evidence cannot answer). Name that question in the ledger before executing anything.
2. Choose the instrument:
   - **Frida** (optional dependency) for runtime instrumentation: hook selection from the static record, minimal surface first, expand only against a concrete gap.
   - **Debuggers** — LLDB and the GDB/pwndbg surface, plus Rizin debug: breakpoints and state inspection for native targets; pwntools supports the offline/exploit-research side of the workflow.
   - **Process capture** for passive runtime evidence: capture what the process does (files, network, children) under the declared lifecycle.
   - **Electron/browser live targets** route through re-web-network-analysis for their connect/launch discipline.
3. Declare the lifecycle before starting: the exact target, the exact actions, and their bounds come from the request scope. Runtime requests execute the declared target and lifecycle — never broaden the target or action beyond those fields mid-run.
4. Prefer recorded crashes when the question is a crash: `inspect_recorded_crash` reads a supplied Linux x86-64 ELF core offline — every recorded thread, raw note, and source-bound register — without opening a live target. Historical PIDs in a core do not select live processes. Request `include_debugger_context` only when core-only mapping candidates help.
5. Reconcile with the static record: runtime observations corroborate or contradict static findings; `correlate_static_and_runtime` (re-version-comparison) uses explicit mappings, and matching patterns are hypotheses, not causality.

## Safety gates

- No gate decision, no execution. No throwaway environment, no execution. Both are checked before the first instrument attaches.
- Tool contracts flag executing operations (`executesForeignCode`, destructive hints); the host client's confirmation is the operative per-call control — never script around it.
- Anything the target does to the environment is contained by the environment's disposability; findings about the target's behavior cite the environment in the record.

## Output contract

- Runtime Evidence records labeled as observations, with instrument and lifecycle named
- Crash analysis records for core-based work

## Related skills

- re-safety-gate — the authorizing gate for this entire lane
- re-web-network-analysis — browser/Electron runtime and capture surfaces
- re-engine-bridges — the static deep lane whose findings seed runtime questions

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-dynamic-analysis/tests -v
git diff --check
```
