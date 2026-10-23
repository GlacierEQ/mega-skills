---
name: re-native-static-readers
description: "REA's built-in target-free native readers: PE/ELF structure and layout, PE certificates and resources, ELF notes, native exports, Go build metadata, Rust cargo-auditable dependencies, CPython pyc, Erlang BEAM, and SQLite snapshots — portable inspection with no engine and no execution."
---

# RE Native Static Readers

Own the built-in reader lane. REA ships a family of target-free inspectors that need no disassembler, no runtime, and no installation of the target's toolchain — they parse structure and report facts with raw locations. Most structural questions end here; engines are for when structure is not enough.

## The readers (each returns Evidence with limitations)

**Live in rea-agents 6.7.0** (verified against the 207-tool surface):

- **Layout & diagnostics** — `inspect_binary_layout` on a Linux ELF (via caller-supplied pwntools): offline layout, symbols, relocations, and static mitigation evidence, without opening a disassembler database.
- **PE resources** — `inspect_pe_resources` (resource type/name/language trees; opaque payloads keep file ranges and SHA-256). `inspect_with_objdump` covers PE/ELF header and section questions through caller-supplied binutils.
- **Go** — `inspect_go_binary`: embedded compiler, module, and build-setting metadata with raw module bytes and source ranges preserved. Absent metadata does not prove a binary is not Go.
- **Rust** — `inspect_rust_binary`: embedded cargo-auditable dependency metadata (`.dep-v0`) from ELF, PE, or thin Mach-O — package order, versions, sources, dependency indices. A missing section is null metadata, not proof of no dependencies; a rustc commit hash inferred from a `/rustc/<40-hex>/` path stays labeled an inference.
- **SQLite** — `inspect_sqlite_database`: schema first (compact inventory by default), selected-table rows on request, database and sibling WAL identities preserved. Inspect a quiescent snapshot; never assume a live WAL pair was copied atomically.

**Not exposed in 6.7.0** — these services exist in REA's source tree but are wired to no MCP tool or CLI command in the pinned release; the lane is carried by this skill's local readers (`scripts/readers.py`) with the same discipline:

- **PE certificates** — Authenticode certificate table (WIN_CERTIFICATE ranges, payload SHA-256, PKCS#7 signer/X.509 identity). A missing security directory is observed absence of the table, not proof an image is unsigned in every catalog sense; signatures are not verified.
- **Native exports** — PE export directories and ELF dynamic symbols (the ELF side is also covered live by `inspect_binary_layout`).
- **ELF notes** — PT_NOTE/SHT_NOTE ranges, owners, types, descriptor SHA-256, GNU build-id and ABI-tag fields. A missing table is absence of those declarations, not proof the image never carried notes.
- **CPython pyc** (3.7–3.13) — header, PEP 552 hash or mtime/size provenance, nested marshal code objects, bytecode SHA-256. Bytecode is not decompiled; a decoded header does not prove the matching `.py` exists.
- **Erlang BEAM** — IFF chunks, atom order, export/import/lambda tables, Code header. Bytecode is not executed; missing optional tables stay null.

## Workflow

1. Triage names the reader (re-target-triage); call it with the explicit path — target-free tools need no `open_binary` session.
2. Preserve raw locations and digests in the ledger exactly as returned; interpretations cite them, never replace them.
3. State each reader's coverage limit beside its findings (absence-of-table is not absence-of-property).
4. Escalate to re-engine-bridges only when the question needs pseudocode or cross-references structure cannot give.

## Safety gates

- These readers never execute the artifact — keep it that way; a request to "just run it and see" routes to re-dynamic-analysis.
- Certificate and signing material is identity evidence, not a trust verdict.

## Output contract

- Reader Evidence records with raw ranges and digests
- Structural findings with per-reader limitations stated

## Related skills

- re-target-triage — routes native artifacts here first
- re-engine-bridges — the escalation lane for decompilation
- re-managed-dotnet — the managed counterpart lane

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-native-static-readers/tests -v
git diff --check
```
