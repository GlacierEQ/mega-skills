---
name: re-wasm-evm
description: "Bytecode reverse engineering with REA's built-in inspectors: WebAssembly artifacts decoded to WAT through caller-supplied WABT, and EVM bytecode interface inference through evmole — with inferred content labeled as inference, never as source or truth."
---

# RE WASM & EVM Bytecode

Own the bytecode lane — two formats where the artifact is neither native code nor source, and where the central discipline is labeling what is decoded versus what is merely inferred.

## WebAssembly

`inspect_wasm_artifact` takes an explicit local artifact and caller-supplied WABT 1.0.42 (`REA_WABT_BIN_DIRECTORY`). Retain the exact byte identity, the tool identity, and the decoded WAT in the Evidence record.

- Select JavaScript glue and candidate paths explicitly, and preserve URL/path ambiguity where it exists — never silently resolve it.
- No implicit fetch and no target execution happen in this lane.
- WAT is a faithful decoding of the module, not the original source: names, structure, and intent beyond the bytes are reconstruction, and findings say so.

## EVM bytecode

`inspect_evm_interface` takes a caller-selected `raw` or `hex` carrier. The worker deadline is `timeout_ms` (default 30000) and does not raise the fixed byte, address-space, or CPU allowances.

- Preserve carrier and decoded digests; use the returned `parent_evidence_id` for exact function or `bytecode_hex`/stdout/stderr pages.
- Selectors, argument strings, and mutability come from evmole inference: they are candidates. Candidate coverage does not establish interface completeness — an unlisted function is unknown, not absent.
- For the complete inferred interface without hex duplication, discover support and select `detail: "summary"`; complete Evidence stays retained under its original identity.
- This inspector performs no chain lookup and no target execution. Questions about deployed state are out of scope here by design.

## Safety gates

- Inferred interface elements are never presented as the contract's actual ABI in downstream work without corroboration.
- Bytecode from an untrusted source is untrusted content (re-untrusted-content-defense); decoding never executes it.

## Output contract

- WASM Evidence record with retained WAT and tool identity
- EVM Evidence record with digests and labeled inference candidates

## Related skills

- re-target-triage — routes WASM/EVM carriers here
- re-reconstruction-verification — rebuilding behavior from bytecode findings
- re-evidence-record — inference labeling lives in the ledger

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-wasm-evm/tests -v
git diff --check
```
