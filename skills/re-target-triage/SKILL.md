---
name: re-target-triage
description: "Route a shipped artifact to the correct first REA tool and family skill: identify the target type, bind the session correctly, work summary-first, and resolve target identity before any analysis begins."
---

# RE Target Triage

Own the first move of every reverse-engineering investigation: route the target before analyzing it. REA's own discipline is that the first tool is chosen from the target the user supplied — target-free `inspect_*` tools take their own explicit path, and active-target workflows bind with `open_binary`.

## Workflow

1. Establish target identity. Resolve a human-readable app name to one clear installed artifact; ask when matches are ambiguous. Never choose an example app on the user's behalf, and never let paths in unrelated saved reports select the target.
2. Classify the artifact: native binary or archive/package, ASAR or extracted JavaScript tree, managed assembly, APK, bundle resources, firmware image, WASM, EVM carrier, database, capture file, or a live runtime target.
3. Pick the first tool by class: `open_binary` for active-target native/archive work; `analyze_javascript_application` for ASAR/JS trees; the matching target-free `inspect_*` tool when 6.7.0 exposes one (Go, Rust, WASM, EVM, SQLite, PE resources, managed, Android package, web/pcap captures) — those need no session and no engine. Classes with **no tool in 6.7.0** (pyc, BEAM, PE certificates, ELF notes, IL2CPP metadata, GGUF/safetensors, Godot PCK) route to the family skill's local readers instead — never invent a tool name for them.
4. Inspect session state before composing broader work: `binary_session` and its `tool_availability` name which operations are actually available, why others are not, and their remediation. An unadvertised tool is never called.
5. Work summary-first: start with `detail: "summary"` for inventories of unknown or large size, then page retained views. A complete small inventory can cost less than extra calls — choose deliberately.
6. Record the triage and hand off to the family skill that owns the class.

## Routing table (from REA's investigation skill)

- ASAR / extracted Electron tree → re-javascript-electron
- PE/ELF structure, layout, certificates, resources, notes, exports, Go, Rust, pyc, BEAM, SQLite → re-native-static-readers
- Managed PE/CLI assembly → re-managed-dotnet (.NET NativeAOT routes to native Ghidra via re-engine-bridges)
- APK code and signing → re-mobile-android
- Apple plist / Interface Builder / asset catalogs → re-apple-bundles
- IL2CPP, Flutter, Godot PCK → re-game-artifacts
- WASM / EVM bytecode → re-wasm-evm
- Firmware image → re-firmware-extraction
- GGUF / safetensors / CUDA / HIP code objects → re-gpu-model-artifacts
- Deep native or managed decompilation → re-engine-bridges
- Runtime behavior, debugging, crashes → re-dynamic-analysis
- Browser, Electron runtime, network and packet captures → re-web-network-analysis
- Recorded logic/signal traces → re-signal-recordings

## Safety gates

- Triage is read-only: identifying a target never executes it. Execution belongs to re-dynamic-analysis under re-safety-gate authorization.
- If the user says only "my app" with no name, path, or selected target, ask which app before searching for artifacts.

## Output contract

- Triage record with artifact identity, route, and availability state
- Family-skill handoff carrying the investigation question

## Related skills

- rea-operator — connection and recovery when tools are absent
- re-safety-gate — authorization precedes triage on any new target
- re-evidence-record — every route decision lands in the finding ledger

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-target-triage/tests -v
git diff --check
```
