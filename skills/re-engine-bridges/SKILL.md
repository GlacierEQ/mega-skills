---
name: re-engine-bridges
description: "Deep decompilation through REA's bring-your-own engine bridges: Ghidra headless (ephemeral project), IDA Pro (read-only, owned headless database), Hopper, Cutter/Rizin, JEB, and the Kuna cached-export provider — provider selection, session hygiene, and per-engine evidence limits."
---

# RE Engine Bridges

Own the bridge lane. REA installs no analysis engines — it drives the operator's own Ghidra, IDA Pro, Hopper, Cutter/Rizin, JEB, or Kuna through authenticated bridges and returns their output as Evidence. Choosing the provider, and knowing what each provider's output can and cannot establish, is this skill's work.

## The providers

- **Ghidra** (the default deep lane): a Java bridge drives headless analysis in an isolated temporary project with a private home/cache/runtime; the project is deleted when the session closes and user-owned Ghidra projects are never opened or modified. Architecture coverage includes x86, MIPS, PowerPC, PSP, RISC-V, and DOS-era targets, with a NativeAOT workflow for .NET NativeAOT binaries. For a startup timeout on a large target, follow the deadline-recovery procedure (default 330s, configurable; changing it requires a new REA process) before abandoning deep analysis or repeating the same cold import.
- **IDA Pro**: use `open_binary` with the original input binary and `provider_id: "ida"` — never an `.idb`/`.i64`. The modern headless profile creates and closes an owned private database without saving; the legacy attached profile binds the already-open GUI input by SHA-256 and leaves its database open. IDA analysis is read-only. Proceed directly to `analyze_function`, pseudocode, and function/string searches — IDA does not supply `binary_overview`. Registration reuses mrexodia/ida-pro-mcp.
- **Hopper**: a Python bridge to the operator's Hopper install. On Linux, REA accepts release metadata only from Hopper's HTTPS endpoint, bounds package size, and compares downloaded bytes against the published checksum before requesting installation (HTTPS origin validation is part of the trust boundary).
- **Cutter/Rizin**: the Rizin-based lane for interactive-grade native inspection and its debug surface (debug work itself routes to re-dynamic-analysis).
- **JEB**: connected by MCP URL for Android/managed deep work.
- **Kuna**: with `REA_KUNA_COMMAND` configured, `provider_id: "kuna"` answers procedure lists, lookups, pseudocode, assembly, and `analyze_function` from Kuna's cached whole-program export; callers/callees use a body-free session graph and `xrefs` returns exact-address incoming sites. Indirect targets remain unknown and can make relationship coverage partial; typed references, CFG, raw-memory tools, and annotations are unsupported. A cold first answer may come from a single-function run — its limitations say so.

## Workflow

1. Exhaust the built-in readers first (re-native-static-readers); escalate only when the question needs pseudocode, xrefs, or a call graph.
2. Select the provider from target class and available licenses; record the selection rationale and the provider's known blind spots for this target.
3. Open through REA (`open_binary` with the provider), work from `analyze_function` and focused searches; consult session availability before composing broader workflows.
4. Keep provider scopes distinct in the ledger: provider candidate facts, session capabilities, and the selected binding are not interchangeable, and live IDA results are not replayed from snapshots.
5. Close the session (`close_binary`) when the investigation completes; ephemeral projects die with it.

## Safety gates

- Bridges authenticate with per-session random capability tokens (Unix sockets; private NTFS runtime on Windows) — tokens never appear in reports or logs.
- REA is not a sandbox (re-safety-gate): opening a hostile binary delegates parsing to the engine with the operator's permissions. Unknown targets get the throwaway environment.
- Commercial engines are the operator's license problem — REA grants none, and neither does this skill.

## Output contract

- Provider Evidence records with addresses and provider identity
- Provider selection note with blind spots recorded

## Related skills

- re-native-static-readers — the first lane for native structure
- re-managed-dotnet — managed targets and the NativeAOT routing rule
- re-dynamic-analysis — debugging surfaces (GDB/Rizin debug) live there

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-engine-bridges/tests -v
git diff --check
```
